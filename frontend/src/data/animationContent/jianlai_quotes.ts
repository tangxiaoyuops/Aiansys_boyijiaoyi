/**
 * 剑来语录 - 哲理故事内容
 */
import { ContentType, AnimationType, AnimationContent } from '@/types/animation';

export const jianLaiQuotes: AnimationContent = {
  id: 'wisdom-002',
  title: '剑来·语录',
  type: ContentType.WISDOM,
  duration: 90,
  author: '烽火戏诸侯',
  source: '《剑来》',
  tags: ['剑来', '恋爱观', '语录'],
  background: {
    type: 'snow',
    value: {
      colors: ['#e3f2fd', '#bbdefb', '#90caf9'],
      animated: true
    }
  },
  scenes: [
    {
      id: 'scene-1',
      type: 'title',
      content: '剑来·语录',
      animation: AnimationType.FADE_IN,
      duration: 2000,
      style: {
        fontSize: '44px',
        color: '#1565c0',
        textAlign: 'center',
        fontWeight: '600'
      }
    },
    {
      id: 'scene-2',
      type: 'quote',
      content: '不被喜欢的姑娘喜欢是一件很伤心的事情，可天没有塌下来，该怎么活还得怎么活，一位好的姑娘不喜欢你，一定是因为你还不够好。',
      animation: AnimationType.TYPEWRITER,
      duration: 6000,
      style: {
        fontSize: '22px',
        color: '#0d47a1',
        textAlign: 'center'
      }
    },
    {
      id: 'scene-3',
      type: 'quote',
      content: '世间唯有痴情，不容他人取笑。',
      animation: AnimationType.TYPEWRITER,
      duration: 4000,
      style: {
        fontSize: '26px',
        color: '#1565c0',
        textAlign: 'center',
        fontWeight: '500'
      }
    },
    {
      id: 'scene-4',
      type: 'quote',
      content: '一个姑娘，如果有被人喜欢，而且那个人喜欢的干干净净，怎么都是一件美好的事情啊。',
      animation: AnimationType.TYPEWRITER,
      duration: 5000,
      style: {
        fontSize: '22px',
        color: '#0d47a1',
        textAlign: 'center'
      }
    },
    {
      id: 'scene-5',
      type: 'quote',
      content: '喜欢一个人，总得让她开心吧，如果觉得喜欢谁，谁就一定要跟自己在一起，那还叫喜欢吗？',
      animation: AnimationType.TYPEWRITER,
      duration: 5000,
      style: {
        fontSize: '22px',
        color: '#1565c0',
        textAlign: 'center'
      }
    },
    {
      id: 'scene-6',
      type: 'quote',
      content: '不敢说这辈子只喜欢一个姑娘，但绝对不会同时喜欢两个。',
      animation: AnimationType.TYPEWRITER,
      duration: 4500,
      style: {
        fontSize: '24px',
        color: '#0d47a1',
        textAlign: 'center'
      }
    },
    {
      id: 'scene-7',
      type: 'quote',
      content: '我是否喜欢谁，与谁喜不喜欢我，半颗铜钱关系都没有。就像山看水，水流山还在，喜欢之人只管远去，我只管喜欢。',
      animation: AnimationType.TYPEWRITER,
      duration: 6000,
      style: {
        fontSize: '20px',
        color: '#1565c0',
        textAlign: 'center'
      }
    },
    {
      id: 'scene-8',
      type: 'quote',
      content: '只是两个人相处，那么喜欢一个人，可能会觉得她所有都好；但是以后在一起了，就要学会喜欢她的不好。',
      animation: AnimationType.TYPEWRITER,
      duration: 5500,
      style: {
        fontSize: '20px',
        color: '#0d47a1',
        textAlign: 'center'
      }
    },
    {
      id: 'scene-9',
      type: 'quote',
      content: '我喜欢你，不比你喜欢我少一点点。',
      animation: AnimationType.TYPEWRITER,
      duration: 3500,
      style: {
        fontSize: '28px',
        color: '#1565c0',
        textAlign: 'center',
        fontWeight: '500'
      }
    },
    {
      id: 'scene-10',
      type: 'quote',
      content: '浩然天下所有好看的山，好看的水，加在一起，都不如她好看！',
      animation: AnimationType.TYPEWRITER,
      duration: 4500,
      style: {
        fontSize: '24px',
        color: '#0d47a1',
        textAlign: 'center'
      }
    },
    {
      id: 'scene-11',
      type: 'quote',
      content: '喜欢一个人，会喜欢到觉得那个姑娘这辈子都不会喜欢自己，而且不会觉得有任何委屈。',
      animation: AnimationType.TYPEWRITER,
      duration: 5500,
      style: {
        fontSize: '22px',
        color: '#1565c0',
        textAlign: 'center'
      }
    }
  ],
  createdAt: '2026-04-25T11:00:00Z',
  updatedAt: '2026-04-25T11:00:00Z'
};

export default jianLaiQuotes;
