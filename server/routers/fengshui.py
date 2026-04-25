"""
风水布局分析API路由
提供风水分析、朝向查询、工位分析等接口
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import asyncio

from core.agents.fengshui_analysis_agent import fengshui_complete_analysis
from core.agents.fengshui_orientation_agent import fengshui_orientation_analysis
from core.agents.fengshui_layout_agent import fengshui_layout_analysis
from core.agents.fengshui_room_agent import fengshui_room_analysis
from core.agents.fengshui_desk_agent import fengshui_desk_analysis
from core.tools.fengshui_calculator import (
    calculate_bazhai_mingua,
    calculate_orientation_score,
    calculate_yearly_feixing,
)

router = APIRouter(prefix="/api/fengshui", tags=["风水布局分析"])


# ==================== 请求模型 ====================

class FengshuiRequest(BaseModel):
    """完整风水分析请求"""
    birth_year: int
    gender: str
    house_shape: Optional[str] = "矩形"
    house_direction: Optional[str] = "子"
    construction_year: Optional[int] = None
    room_layout: Optional[Dict[str, Any]] = None
    room_types: Optional[List[str]] = None
    occupation_type: Optional[str] = "管理"
    room_size: Optional[Dict[str, float]] = None
    include_layout: Optional[bool] = True
    include_orientation: Optional[bool] = True
    include_room: Optional[bool] = True
    include_desk: Optional[bool] = True
    include_llm: Optional[bool] = False
    analysis_style: Optional[str] = "classic"


class OrientationRequest(BaseModel):
    """朝向分析请求"""
    birth_year: int
    gender: str
    house_direction: str
    include_bazhai: Optional[bool] = True
    include_xuankong: Optional[bool] = True
    construction_year: Optional[int] = None


class MinguaRequest(BaseModel):
    """命卦计算请求"""
    birth_year: int
    gender: str


class LayoutRequest(BaseModel):
    """格局分析请求"""
    house_shape: str
    house_direction: Optional[str] = "子"
    room_layout: Optional[Dict[str, Any]] = None
    include_defect_analysis: Optional[bool] = True
    include_liuxian: Optional[bool] = True


class RoomRequest(BaseModel):
    """房间定位请求"""
    birth_year: int
    gender: str
    house_layout: Optional[Dict[str, Any]] = None
    room_types: Optional[List[str]] = None
    include_feixing: Optional[bool] = False
    construction_year: Optional[int] = None


class DeskRequest(BaseModel):
    """工位分析请求"""
    birth_year: int
    gender: str
    room_direction: str
    occupation_type: Optional[str] = "管理"
    room_size: Optional[Dict[str, float]] = None
    existing_furniture: Optional[List[Dict[str, Any]]] = None


class YearlyFeixingRequest(BaseModel):
    """流年飞星请求"""
    year: int


# ==================== API端点 ====================

@router.post("/analyze")
async def analyze_fengshui(request: FengshuiRequest) -> Dict[str, Any]:
    """
    完整风水分析
    
    综合分析房屋朝向、格局、房间定位、工位摆放等
    """
    try:
        print(f"[API] 收到风水分析请求: 出生{request.birth_year}年, 性别{request.gender}")
        
        house_info = {
            'house_shape': request.house_shape,
            'house_direction': request.house_direction,
            'construction_year': request.construction_year,
            'room_layout': request.room_layout or {},
            'room_types': request.room_types or ['主卧', '书房', '客厅', '厨房', '卫生间'],
            'occupation_type': request.occupation_type,
            'room_size': request.room_size,
        }
        
        result = fengshui_complete_analysis(
            birth_year=request.birth_year,
            gender=request.gender,
            house_info=house_info,
            include_layout=request.include_layout,
            include_orientation=request.include_orientation,
            include_room=request.include_room,
            include_desk=request.include_desk,
            include_llm=request.include_llm,
            analysis_style=request.analysis_style,
        )
        
        if result.get('success'):
            return {
                'success': True,
                'message': '风水分析完成',
                'data': result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', '风水分析失败')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"风水分析执行异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/orientation")
async def analyze_orientation(request: OrientationRequest) -> Dict[str, Any]:
    """
    朝向与坐山立向分析
    
    计算命卦、八宅吉凶方位、朝向适配度评分
    """
    try:
        print(f"[API] 收到朝向分析请求: 出生{request.birth_year}年, 朝向{request.house_direction}")
        
        result = fengshui_orientation_analysis(
            birth_year=request.birth_year,
            gender=request.gender,
            house_direction=request.house_direction,
            include_bazhai=request.include_bazhai,
            include_xuankong=request.include_xuankong,
            construction_year=request.construction_year,
        )
        
        if result.get('success'):
            return {
                'success': True,
                'message': '朝向分析完成',
                'data': result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', '朝向分析失败')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"朝向分析执行异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/mingua")
async def calculate_mingua(request: MinguaRequest) -> Dict[str, Any]:
    """
    八宅命卦计算
    
    根据出生年份和性别计算命卦、东四/西四命、四吉四凶方位
    """
    try:
        print(f"[API] 收到命卦计算请求: 出生{request.birth_year}年, 性别{request.gender}")
        
        result = calculate_bazhai_mingua(request.birth_year, request.gender)
        
        if result.get('success'):
            return {
                'success': True,
                'message': '命卦计算完成',
                'data': result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', '命卦计算失败')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"命卦计算执行异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/layout")
async def analyze_layout(request: LayoutRequest) -> Dict[str, Any]:
    """
    房屋格局分析
    
    分析房屋形状、缺角凸角、格局评分
    """
    try:
        print(f"[API] 收到格局分析请求: 形状{request.house_shape}")
        
        result = fengshui_layout_analysis(
            house_shape=request.house_shape,
            house_direction=request.house_direction,
            room_layout=request.room_layout,
            include_defect_analysis=request.include_defect_analysis,
            include_liuxian=request.include_liuxian,
        )
        
        if result.get('success'):
            return {
                'success': True,
                'message': '格局分析完成',
                'data': result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', '格局分析失败')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"格局分析执行异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/room")
async def analyze_room(request: RoomRequest) -> Dict[str, Any]:
    """
    房间功能定位分析
    
    根据命卦分析各房间的最佳位置
    """
    try:
        print(f"[API] 收到房间定位请求: 出生{request.birth_year}年")
        
        mingua_result = calculate_bazhai_mingua(request.birth_year, request.gender)
        if not mingua_result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=mingua_result.get('error', '命卦计算失败')
            )
        
        room_types = request.room_types or ['主卧', '书房', '客厅', '厨房', '卫生间']
        
        result = fengshui_room_analysis(
            house_layout=request.house_layout or {},
            mingua=mingua_result['mingua'],
            room_types=room_types,
            include_feixing=request.include_feixing,
        )
        
        if result.get('success'):
            return {
                'success': True,
                'message': '房间定位完成',
                'data': result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', '房间定位失败')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"房间定位执行异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/desk")
async def analyze_desk(request: DeskRequest) -> Dict[str, Any]:
    """
    工位/办公桌摆放分析
    
    根据命卦和职业类型分析办公桌最佳摆放位置
    """
    try:
        print(f"[API] 收到工位分析请求: 出生{request.birth_year}年, 职业{request.occupation_type}")
        
        mingua_result = calculate_bazhai_mingua(request.birth_year, request.gender)
        if not mingua_result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=mingua_result.get('error', '命卦计算失败')
            )
        
        result = fengshui_desk_analysis(
            room_direction=request.room_direction,
            mingua=mingua_result['mingua'],
            occupation_type=request.occupation_type,
            room_size=request.room_size,
            existing_furniture=request.existing_furniture,
        )
        
        if result.get('success'):
            return {
                'success': True,
                'message': '工位分析完成',
                'data': result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', '工位分析失败')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"工位分析执行异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/yearly-feixing")
async def get_yearly_feixing(request: YearlyFeixingRequest) -> Dict[str, Any]:
    """
    流年飞星查询
    
    获取指定年份的九宫飞星分布
    """
    try:
        print(f"[API] 收到流年飞星请求: {request.year}年")
        
        result = calculate_yearly_feixing(request.year)
        
        if result.get('success'):
            return {
                'success': True,
                'message': '流年飞星查询完成',
                'data': result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', '流年飞星查询失败')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"流年飞星查询异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.post("/llm-stream")
async def llm_stream_analysis(request: FengshuiRequest):
    """
    流式LLM分析（SSE）
    
    返回流式AI深度解读
    """
    try:
        print(f"[API] 收到流式LLM分析请求")
        
        async def generate_stream():
            from core.tools.llm_client import call_llm_stream
            from core.agents.fengshui_prompt_styles import get_fengshui_prompt
            
            house_info = {
                'house_shape': request.house_shape,
                'house_direction': request.house_direction,
                'construction_year': request.construction_year,
                'room_layout': request.room_layout or {},
                'room_types': request.room_types or ['主卧', '书房', '客厅', '厨房', '卫生间'],
                'occupation_type': request.occupation_type,
                'room_size': request.room_size,
            }
            
            result = fengshui_complete_analysis(
                birth_year=request.birth_year,
                gender=request.gender,
                house_info=house_info,
                include_layout=request.include_layout,
                include_orientation=request.include_orientation,
                include_room=request.include_room,
                include_desk=request.include_desk,
                include_llm=False,
                analysis_style=request.analysis_style,
            )
            
            if not result.get('success'):
                yield f"data: {json.dumps({'error': result.get('error', '分析失败')})}\n\n"
                return
            
            system_prompt, user_prompt = get_fengshui_prompt(result, request.analysis_style)
            
            try:
                for chunk in call_llm_stream(system_prompt, user_prompt):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                    await asyncio.sleep(0.01)
                
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        error_msg = f"流式LLM分析异常: {str(e)}"
        print(f"[API] {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/directions")
async def get_supported_directions() -> Dict[str, Any]:
    """
    获取支持的房屋朝向列表
    
    返回二十四山列表
    """
    from core.tools.fengshui_calculator import ERSHISI_SHAN, SHAN_DEGREES
    
    directions = []
    for gua, shan_list in ERSHISI_SHAN.items():
        for shan in shan_list:
            degrees = SHAN_DEGREES.get(shan, (0, 15))
            directions.append({
                'shan': shan,
                'gua': gua,
                'degrees_start': degrees[0],
                'degrees_end': degrees[1],
            })
    
    return {
        'success': True,
        'message': '获取朝向列表成功',
        'data': {
            'directions': directions,
            'total': len(directions),
        }
    }


@router.get("/occupations")
async def get_supported_occupations() -> Dict[str, Any]:
    """
    获取支持的职业类型列表
    
    返回职业类型及其五行属性
    """
    from core.tools.fengshui_calculator import OCCUPATION_WUXING
    
    occupations = []
    for occupation, wuxing in OCCUPATION_WUXING.items():
        occupations.append({
            'name': occupation,
            'wuxing': wuxing,
        })
    
    return {
        'success': True,
        'message': '获取职业类型成功',
        'data': {
            'occupations': occupations,
            'total': len(occupations),
        }
    }
