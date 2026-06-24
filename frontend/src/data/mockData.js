/**
 * mockData.js — 工厂函数，为 Coding Coach 考试平台提供真实感 Mock 数据。
 * 所有用户可见文本均为中文。
 */

// ---------------------------------------------------------------------------
// 1. 挑战列表
// ---------------------------------------------------------------------------
export function getChallenges() {
  return [
    {
      filename: 'deep-face-search',
      title: 'Deep Face Search',
      icon: '🔍',
      difficulty: 'medium',
      tags: ['AI', 'Python'],
      passRate: 72,
      attemptCount: 156,
      status: 'solved',
      description: '基于深度特征向量的人脸搜索系统，综合考察嵌入模型训练与近似最近邻检索（ANN）的工程落地能力。'
    },
    {
      filename: 'advanced-short-url',
      title: '高并发短链接系统',
      icon: '🔗',
      difficulty: 'medium',
      tags: ['Redis', '高并发'],
      passRate: 64,
      attemptCount: 98,
      status: 'attempted',
      description: '设计并实现一个支持高并发读写的短链接服务，涉及分布式 ID 生成、缓存策略与数据持久化方案。'
    },
    {
      filename: 'vibe-coding-challenge',
      title: '运筹优化挑战',
      icon: '📊',
      difficulty: 'hard',
      tags: ['ODPS', '运筹'],
      passRate: 45,
      attemptCount: 67,
      status: 'new',
      description: '基于 ODPS 平台的运筹优化问题，需要设计高效的分配算法处理大规模资源约束，考察数学建模与工程实现能力。'
    },
    {
      filename: 'lru-cache',
      title: 'LRU 缓存设计',
      icon: '🗂️',
      difficulty: 'easy',
      tags: ['数据结构'],
      passRate: 85,
      attemptCount: 234,
      status: 'solved',
      description: '实现一个支持 O(1) 时间复杂度的 LRU（最近最少使用）缓存结构，考察哈希表与双向链表的组合运用能力。'
    },
    {
      filename: 'realtime-stream',
      title: '实时流处理管道',
      icon: '⚡',
      difficulty: 'medium',
      tags: ['Kafka', '流处理'],
      passRate: 58,
      attemptCount: 89,
      status: 'new',
      description: '构建基于 Kafka 的实时数据流处理管道，涉及消息分区策略、Exactly-Once 语义保证以及下游消费容错机制。'
    },
    {
      filename: 'distributed-lock',
      title: '分布式锁实现',
      icon: '🔒',
      difficulty: 'hard',
      tags: ['Redis', 'Go'],
      passRate: 38,
      attemptCount: 45,
      status: 'attempted',
      description: '用 Go 语言基于 Redis 实现一个可靠的分布式锁，需要处理锁续约、Redlock 算法、以及网络分区场景下的安全性保障。'
    }
  ]
}

// ---------------------------------------------------------------------------
// 2. 用户信息
// ---------------------------------------------------------------------------
export function getUserProfile() {
  return {
    name: '王五',
    email: 'wangwu@example.com',
    avatar: '',
    tags: ['Python', '算法', '后端开发', 'AI 爱好者'],
    solved: 24,
    attempted: 36,
    passRate: 67,
    totalSubmissions: 128,
    examsTaken: 5,
    bestRank: 12,
    studyDays: 89
  }
}

// ---------------------------------------------------------------------------
// 3. 最近动态
// ---------------------------------------------------------------------------
export function getUserActivities() {
  return [
    {
      type: 'pass',
      title: '通过了 Deep Face Search',
      time: '2026-06-21 14:32',
      result: '得分 88 / 100'
    },
    {
      type: 'start',
      title: '开始挑战 运筹优化挑战',
      time: '2026-06-20 09:15',
      result: ''
    },
    {
      type: 'fail',
      title: '未通过 分布式锁实现',
      time: '2026-06-18 16:40',
      result: '得分 42 / 100'
    },
    {
      type: 'pass',
      title: '通过了 LRU 缓存设计',
      time: '2026-06-15 11:00',
      result: '得分 95 / 100'
    },
    {
      type: 'start',
      title: '开始挑战 实时流处理管道',
      time: '2026-06-14 10:30',
      result: ''
    },
    {
      type: 'fail',
      title: '未通过 高并发短链接系统',
      time: '2026-06-10 15:22',
      result: '得分 51 / 100'
    },
    {
      type: 'pass',
      title: '通过了 实时流处理管道',
      time: '2026-06-08 13:45',
      result: '得分 76 / 100'
    }
  ]
}

// ---------------------------------------------------------------------------
// 4. 成绩报告
// ---------------------------------------------------------------------------
export function getScoreReport(filename) {
  const reports = {
    'deep-face-search': {
      totalScore: 88,
      maxScore: 100,
      grade: 'A',
      resultScore: 52,
      resultMax: 60,
      passed: true,
      processScores: [
        { icon: '📝', label: '需求分析', score: 18, max: 20 },
        { icon: '🏗️', label: '架构设计', score: 17, max: 20 },
        { icon: '💻', label: '代码实现', score: 35, max: 40 },
        { icon: '✅', label: '测试覆盖', score: 18, max: 20 }
      ],
      testCases: [
        { name: '基础搜索功能', passed: true, message: '通过' },
        { name: '大规模数据集性能', passed: true, message: '通过' },
        { name: '边界条件处理', passed: true, message: '通过' },
        { name: '多维度特征融合', passed: false, message: '超时：处理时间超过 500ms 限制' }
      ],
      code: `class FaceSearchEngine:
    def __init__(self, dim=512, top_k=5):
        self.dim = dim
        self.top_k = top_k
        self.index = faiss.IndexFlatL2(dim)
        self.faces = []

    def add_face(self, face_vector, metadata):
        self.index.add(face_vector)
        self.faces.append(metadata)

    def search(self, query_vector):
        distances, indices = self.index.search(query_vector, self.top_k)
        return [(self.faces[i], float(distances[0][j]))
                for j, i in enumerate(indices[0]) if i < len(self.faces)]`,
      stats: {
        timeUsed: '45 分钟',
        aiRounds: 12,
        tokens: 8452,
        tokensIn: 4230,
        tokensOut: 4222,
        model: 'Claude-4.5-Opus',
        tabSwitches: 5
      },
      submittedAt: '2026-06-21 14:32',
      submitCount: 3
    },
    'lru-cache': {
      totalScore: 95,
      maxScore: 100,
      grade: 'A',
      resultScore: 57,
      resultMax: 60,
      passed: true,
      processScores: [
        { icon: '📝', label: '需求分析', score: 19, max: 20 },
        { icon: '🏗️', label: '架构设计', score: 18, max: 20 },
        { icon: '💻', label: '代码实现', score: 39, max: 40 },
        { icon: '✅', label: '测试覆盖', score: 19, max: 20 }
      ],
      testCases: [
        { name: 'Put / Get 基本操作', passed: true, message: '通过' },
        { name: '容量上限淘汰', passed: true, message: '通过' },
        { name: 'O(1) 时间复杂度', passed: true, message: '通过' },
        { name: '并发安全', passed: true, message: '通过' }
      ],
      code: `class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)`,
      stats: {
        timeUsed: '22 分钟',
        aiRounds: 6,
        tokens: 3210,
        tokensIn: 1400,
        tokensOut: 1810,
        model: 'Claude-4.5-Opus',
        tabSwitches: 2
      },
      submittedAt: '2026-06-15 11:00',
      submitCount: 1
    }
  }

  // 默认报告，用于未完成的挑战
  return reports[filename] || {
    totalScore: 0,
    maxScore: 100,
    grade: 'D',
    resultScore: 0,
    resultMax: 60,
    passed: false,
    processScores: [
      { icon: '📝', label: '需求分析', score: 0, max: 20 },
      { icon: '🏗️', label: '架构设计', score: 0, max: 20 },
      { icon: '💻', label: '代码实现', score: 0, max: 40 },
      { icon: '✅', label: '测试覆盖', score: 0, max: 20 }
    ],
    testCases: [
      { name: '基础功能测试', passed: false, message: '未提交' }
    ],
    code: '// 尚未提交代码',
    stats: {
      timeUsed: '0 分钟',
      aiRounds: 0,
      tokens: 0,
      tokensIn: 0,
      tokensOut: 0,
      model: '-',
      tabSwitches: 0
    },
    submittedAt: '-',
    submitCount: 0
  }
}

// ---------------------------------------------------------------------------
// 5. 题解列表
// ---------------------------------------------------------------------------
export function getSolutions() {
  return [
    {
      id: 'sol-001',
      problem: 'lru-cache',
      problemIcon: '🗂️',
      difficulty: 'easy',
      title: 'OrderedDict 一招制敌：LRU 缓存的 Python 实现',
      summary: '利用 Python 内置的 collections.OrderedDict 可以极简地实现 LRU 缓存，核心是利用 move_to_end 和 popitem 两个方法维护访问顺序。',
      featured: true,
      author: {
        name: '李四',
        avatar: ''
      },
      time: '2026-06-12',
      likes: 186,
      stars: 52,
      comments: 23,
      tags: ['Python', '数据结构', 'LRU'],
      codePreview: `class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.data = OrderedDict()
    def get(self, key): ...
    def put(self, key, value): ...`,
      fullContent: {
        approach: '本题的核心在于维护数据的访问顺序，并在容量满时淘汰最久未被访问的元素。Python 的 OrderedDict 天然支持按插入顺序遍历，且提供了 move_to_end 方法可在 O(1) 时间内将任意键值对移至末尾（表示最近访问），popitem(last=False) 则可在 O(1) 时间内移除最久未被访问的项。',
        fullCode: `from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)`,
        timeComplexity: '所有操作均为 O(1)',
        spaceComplexity: 'O(capacity)，其中 capacity 为缓存容量上限',
        pitfalls: [
          '直接使用 dict 无法满足 LRU 淘汰需求——普通 dict 虽在 Python 3.7+ 中保持插入顺序，但缺少 move_to_end 的 O(1) 实现。',
          '并发场景下 OrderedDict 不是线程安全的，需要外部加锁。',
          'popitem(last=False) 移除的是最早插入的，不是最久未访问的——必须先 move_to_end 才能正确实现 LRU。'
        ]
      }
    },
    {
      id: 'sol-002',
      problem: 'deep-face-search',
      problemIcon: '🔍',
      difficulty: 'medium',
      title: '从零搭建人脸搜索系统：FAISS + 特征提取实战',
      summary: '本文详细介绍如何使用 FAISS 库构建高性能人脸搜索系统，涵盖特征提取、索引构建、近似搜索优化等关键技术点。',
      featured: false,
      author: {
        name: '张算法',
        avatar: ''
      },
      time: '2026-06-10',
      likes: 134,
      stars: 41,
      comments: 17,
      tags: ['AI', 'Python', 'FAISS', '向量检索'],
      codePreview: `class FaceSearchEngine:
    def __init__(self, dim=512):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
    def add_face(self, vec, meta): ...
    def search(self, query): ...`,
      fullContent: {
        approach: '系统分为三个核心模块：(1) 人脸特征提取——使用预训练的 ArcFace 模型将人脸图像映射为 512 维嵌入向量；(2) 索引构建——利用 FAISS 的 IndexFlatL2 构建精确 L2 距离索引，数据量较大时可升级为 IndexIVFFlat 以加速；(3) 元数据管理——在内存中维护面片 ID 到元数据的映射，搜索结果返回 top_k 最相似人脸及其相似度得分。',
        fullCode: `import faiss
import numpy as np

class FaceSearchEngine:
    def __init__(self, dim=512, top_k=5):
        self.dim = dim
        self.top_k = top_k
        self.index = faiss.IndexFlatL2(dim)
        self.faces = []

    def add_face(self, face_vector, metadata):
        vec = np.array(face_vector, dtype=np.float32).reshape(1, -1)
        self.index.add(vec)
        self.faces.append(metadata)

    def search(self, query_vector):
        q = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(q, self.top_k)
        results = []
        for j, i in enumerate(indices[0]):
            if i >= 0 and i < len(self.faces):
                results.append({
                    'metadata': self.faces[i],
                    'distance': float(distances[0][j])
                })
        return results

    def size(self):
        return len(self.faces)`,
        timeComplexity: '搜索 O(dim * N)（暴力），升级 IndexIVFFlat 后约为 O(dim * sqrt(N))',
        spaceComplexity: 'O(dim * N)，N 为已索引的人数',
        pitfalls: [
          'FAISS 索引不支持删除操作——需要定期重建索引。',
          '特征向量需强转为 float32 类型，否则 FAISS 会报类型错误。',
          'L2 距离受特征尺度影响较大，建议对特征做 L2 归一化后改用内积距离（IndexFlatIP）。'
        ]
      }
    },
    {
      id: 'sol-003',
      problem: 'distributed-lock',
      problemIcon: '🔒',
      difficulty: 'hard',
      title: 'Redlock 算法深度解析与 Go 实现',
      summary: '分布式锁是分布式系统中最基础也最容易出错的组件。本文从单节点 SET NX 开始，逐步演进到多节点 Redlock 算法，并提供生产级 Go 代码实现。',
      featured: false,
      author: {
        name: '赵架构',
        avatar: ''
      },
      time: '2026-06-05',
      likes: 256,
      stars: 89,
      comments: 34,
      tags: ['Go', 'Redis', '分布式', 'Redlock'],
      codePreview: `type RedLock struct {
    clients []*redis.Client
    quorum  int
}
func (r *RedLock) Lock(key string, ttl time.Duration) error { ... }`,
      fullContent: {
        approach: '单节点 Redis 分布式锁存在单点故障问题。Redlock 算法通过在 N 个独立的 Redis 节点（通常 N=5）上协作加锁来解决此问题。加锁时客户端依次向所有节点发送 SET key value NX PX ttl 命令，若超过半数（N/2+1）节点成功获取锁且总耗时小于锁有效期，则认为加锁成功。解锁时向所有节点发送 Lua 脚本释放锁。',
        fullCode: `package redlock

import (
    "crypto/rand"
    "encoding/hex"
    "errors"
    "sync"
    "time"
    "github.com/go-redis/redis/v8"
    "golang.org/x/net/context"
)

var ErrLockFailed = errors.New("redlock: failed to acquire lock")

type RedLock struct {
    clients []*redis.Client
    quorum  int
    mu      sync.Mutex
}

func New(clients []*redis.Client) *RedLock {
    return &RedLock{
        clients: clients,
        quorum:  len(clients)/2 + 1,
    }
}

func (r *RedLock) Lock(ctx context.Context, key string, ttl time.Duration) (string, error) {
    r.mu.Lock()
    defer r.mu.Unlock()

    value := randomValue()
    deadline := time.Now().Add(ttl)
    success := 0

    for _, cli := range r.clients {
        if time.Now().After(deadline) {
            break
        }
        ok, err := cli.SetNX(ctx, key, value, ttl).Result()
        if err != nil || !ok {
            continue
        }
        success++
    }

    if success < r.quorum {
        r.Unlock(ctx, key, value)
        return "", ErrLockFailed
    }
    return value, nil
}

func (r *RedLock) Unlock(ctx context.Context, key, value string) error {
    script := ` + "`" + `
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end` + "`" + `
    for _, cli := range r.clients {
        cli.Eval(ctx, script, []string{key}, value)
    }
    return nil
}

func randomValue() string {
    b := make([]byte, 16)
    rand.Read(b)
    return hex.EncodeToString(b)
}`,
        timeComplexity: '加锁 O(N)，解锁 O(N)，N 为 Redis 节点数',
        spaceComplexity: 'O(1)',
        pitfalls: [
          '时钟漂移（clock drift）是 Redlock 最大的安全隐患——如果某个节点的时钟出现大幅度跳跃，锁安全性会受影响。',
          '网络分区可能导致脑裂：若客户端 A 与多数节点网络正常，但客户端 B 仅与少数节点通信，两个客户端可能同时认为自己持锁。',
          '锁续约（watchdog）是可选但推荐的增强：对于长时间任务，应在后台自动续期锁，避免任务未完成锁已过期。'
        ]
      }
    }
  ]
}

// ---------------------------------------------------------------------------
// 6. 竞赛数据
// ---------------------------------------------------------------------------
export function getContestData() {
  return {
    week: 'Week 24 / 2026',
    title: '2026 夏季编程挑战赛 · 第 3 周',
    theme: '高并发系统设计',
    problemCount: 3,
    timeLimit: 120,
    registered: 326,
    pointsReward: 500,
    completionRate: 68,
    countdown: 3600 * 48 + 1800, // 约 48.5 小时
    problems: [
      {
        name: '分布式限流器',
        tag: 'Redis',
        passRate: 62,
        avgTime: 35,
        status: 'solved',
        acceptance: 128
      },
      {
        name: '消息队列削峰',
        tag: 'Kafka',
        passRate: 48,
        avgTime: 48,
        status: 'attempted',
        acceptance: 67
      },
      {
        name: '读写分离缓存',
        tag: 'MySQL',
        passRate: 55,
        avgTime: 40,
        status: 'new',
        acceptance: 94
      }
    ],
    topRank: [
      { rank: 1, name: 'Alice', avatar: '', solved: 3, time: '85:30', rating: 2280 },
      { rank: 2, name: 'Bob', avatar: '', solved: 3, time: '92:15', rating: 2150 },
      { rank: 3, name: 'Charlie', avatar: '', solved: 3, time: '98:40', rating: 2100 },
      { rank: 4, name: 'Diana', avatar: '', solved: 2, time: '75:20', rating: 2050 },
      { rank: 5, name: 'Eve', avatar: '', solved: 2, time: '88:00', rating: 1980 }
    ],
    history: [
      {
        title: '2026 夏季挑战赛 · 第 2 周',
        date: '2026-06-14',
        problems: 3,
        solved: 2,
        time: '105:20',
        rank: 24,
        rating: 1850
      },
      {
        title: '2026 夏季挑战赛 · 第 1 周',
        date: '2026-06-07',
        problems: 3,
        solved: 1,
        time: '118:00',
        rank: 56,
        rating: 1720
      },
      {
        title: '2026 春季算法赛',
        date: '2026-05-20',
        problems: 4,
        solved: 3,
        time: '140:00',
        rank: 31,
        rating: 1650
      }
    ]
  }
}

// ---------------------------------------------------------------------------
// 7. 排行榜
// ---------------------------------------------------------------------------
export function getLeaderboard() {
  const entry = (rank, name, tier, tierName, rating, change, contests, winRate, peak, recent) => ({
    rank,
    name,
    avatar: '',
    tier,
    tierName,
    rating,
    change,
    contests,
    winRate,
    peak,
    recent
  })

  const entries = [
    entry(1, 'Alice', 'legend', '传奇王者', 2280, 15, 32, 78, 2350, [1, 1, 2, 1, 3]),
    entry(2, 'Bob', 'legend', '传奇王者', 2150, -10, 28, 71, 2200, [2, 3, 1, 4, 2]),
    entry(3, 'Charlie', 'diamond', '钻石', 2100, 25, 19, 63, 2120, [5, 2, 3, 1, 1]),
    entry(4, 'Diana', 'diamond', '钻石', 2050, 8, 22, 68, 2080, [3, 4, 2, 3, 4]),
    entry(5, 'Eve', 'diamond', '钻石', 1980, -5, 15, 60, 2010, [4, 1, 6, 5, 3]),
    entry(6, 'Frank', 'platinum', '铂金', 1920, 30, 26, 65, 1920, [7, 5, 4, 6, 2]),
    entry(7, 'Grace', 'platinum', '铂金', 1890, 12, 18, 58, 1910, [6, 7, 5, 4, 6]),
    entry(8, 'Henry', 'platinum', '铂金', 1860, -8, 14, 55, 1900, [8, 6, 7, 8, 5]),
    entry(9, 'Ivy', 'gold', '黄金', 1820, 18, 20, 52, 1840, [9, 10, 8, 7, 9]),
    entry(10, 'Jack', 'gold', '黄金', 1790, -3, 12, 50, 1810, [10, 9, 10, 9, 8])
  ]

  // 填充到 150 条，让"当前用户"排在 128 名
  for (let i = 11; i <= 127; i++) {
    const names = ['刘洋', '陈思', '杨帆', '周杰', '吴昊', '郑雨', '钱程', '孙悦', '马超', '朱峰']
    const name = names[i % names.length] + (Math.floor(i / names.length) || '')
    entries.push(entry(i, name, 'silver', '白银', 1550 - i * 2, 0, 5 + (i % 10), 45, 1580 - i, [i, i + 1, i - 1, i + 2, i]))
  }

  // 当前用户排在 128
  entries.push(entry(128, '王五', 'silver', '白银', 1280, 45, 8, 42, 1310, [128, 135, 140, 120, 145]))

  for (let i = 129; i <= 150; i++) {
    const names = ['何明', '林婷', '高远', '唐磊', '崔丽']
    const name = names[i % names.length] + (Math.floor(i / names.length) || '')
    entries.push(entry(i, name, 'bronze', '青铜', 1200 - (i - 128) * 3, 0, 3 + (i % 5), 35, 1250 - i, [i, i + 1, i - 1, i + 2, i]))
  }

  return {
    total: entries.length,
    entries
  }
}

// ---------------------------------------------------------------------------
// 8. Rating 趋势
// ---------------------------------------------------------------------------
export function getRatingTrend() {
  return [
    { label: 'W13', value: 1500 },
    { label: 'W14', value: 1580 },
    { label: 'W15', value: 1520 },
    { label: 'W16', value: 1650 },
    { label: 'W17', value: 1620 },
    { label: 'W18', value: 1720 },
    { label: 'W19', value: 1800 },
    { label: 'W20', value: 1750 },
    { label: 'W21', value: 1850 },
    { label: 'W22', value: 1950 },
    { label: 'W23', value: 2100 },
    { label: 'W24', value: 2200 }
  ]
}

// ---------------------------------------------------------------------------
// 9. 考试场次
// ---------------------------------------------------------------------------
export function getExamSessions() {
  return [
    {
      id: 'exam-001',
      name: '2026 春季后端工程师认证考试',
      start: '2026-06-25 09:00',
      end: '2026-06-25 12:00',
      questions: 6,
      participants: { current: 87, total: 120 },
      status: 'upcoming',
      passRate: 62
    },
    {
      id: 'exam-002',
      name: '数据结构与算法专题考核',
      start: '2026-06-22 09:00',
      end: '2026-06-22 17:00',
      questions: 4,
      participants: { current: 56, total: 80 },
      status: 'active',
      passRate: 58
    },
    {
      id: 'exam-003',
      name: 'AI 编程能力测试（5月场）',
      start: '2026-05-15 09:00',
      end: '2026-05-15 16:00',
      questions: 5,
      participants: { current: 104, total: 104 },
      status: 'ended',
      passRate: 49
    },
    {
      id: 'exam-004',
      name: '2026 暑期集训营摸底考试',
      start: '2026-07-01 09:00',
      end: '2026-07-01 11:30',
      questions: 3,
      participants: { current: 0, total: 200 },
      status: 'draft',
      passRate: 0
    }
  ]
}

// ---------------------------------------------------------------------------
// 10. 考试统计摘要
// ---------------------------------------------------------------------------
export function getExamStats() {
  return {
    total: 4,
    active: 1,
    upcoming: 1,
    totalParticipants: 544
  }
}

// ---------------------------------------------------------------------------
// 11. 监考数据
// ---------------------------------------------------------------------------
export function getMonitorData(examId) {
  const baseData = {
    title: examId === 'exam-002' ? '数据结构与算法专题考核' : '未知考试',
    status: 'active',
    online: 56,
    offline: 12,
    submitted: 34,
    alerts: 3,
    timer: '02:15:30',
    questionProgress: [
      { name: 'LRU 缓存设计', progress: 78 },
      { name: '二叉树遍历优化', progress: 52 },
      { name: '图最短路径算法', progress: 35 },
      { name: '动态规划综合题', progress: 18 }
    ],
    containers: [
      { name: 'sandbox-01', cpu: 45, mem: 512, status: 'running' },
      { name: 'sandbox-02', cpu: 62, mem: 768, status: 'running' },
      { name: 'sandbox-03', cpu: 28, mem: 256, status: 'running' },
      { name: 'sandbox-04', cpu: 91, mem: 1024, status: 'warning' },
      { name: 'sandbox-05', cpu: 15, mem: 128, status: 'running' },
      { name: 'sandbox-06', cpu: 0, mem: 0, status: 'stopped' }
    ],
    candidates: [
      { name: '王五', status: 'online', question: '图最短路径算法', completed: 66, timeUsed: '01:48', submits: 8, alert: true },
      { name: '张三', status: 'online', question: 'LRU 缓存设计', completed: 100, timeUsed: '02:12', submits: 3 },
      { name: '李四', status: 'online', question: '二叉树遍历优化', completed: 45, timeUsed: '01:30', submits: 5 },
      { name: '赵六', status: 'offline', question: '动态规划综合题', completed: 20, timeUsed: '00:52', submits: 1 },
      { name: '陈七', status: 'online', question: 'LRU 缓存设计', completed: 88, timeUsed: '02:05', submits: 6 },
      { name: '周八', status: 'online', question: '二叉树遍历优化', completed: 72, timeUsed: '01:55', submits: 4 },
      { name: '吴九', status: 'offline', question: '图最短路径算法', completed: 30, timeUsed: '01:10', submits: 2 },
      { name: '郑十', status: 'online', question: '动态规划综合题', completed: 55, timeUsed: '01:40', submits: 7, alert: true }
    ],
    alertLog: [
      { time: '10:45:22', level: 'warning', text: '王五 - 检测到切屏行为（第 3 次）', action: '已记录' },
      { time: '10:38:15', level: 'info', text: 'sandbox-04 内存使用率超过 90%', action: '已告警' },
      { time: '10:22:08', level: 'warning', text: '郑十 - 提交异常（5 分钟内提交 4 次）', action: '已审查' },
      { time: '10:15:30', level: 'info', text: 'sandbox-06 意外停止，正在重启', action: '已恢复' },
      { time: '10:05:00', level: 'info', text: '考试正式开始', action: '-' }
    ]
  }
  return baseData
}

// ---------------------------------------------------------------------------
// 12. 阅卷数据
// ---------------------------------------------------------------------------
export function getGradingData(examId) {
  const students = [
    { rank: 1, name: '张三', t1: 95, t2: 88, t3: 92, t4: 90, total: 92, status: 'passed' },
    { rank: 2, name: '李四', t1: 90, t2: 85, t3: 78, t4: 82, total: 85, status: 'passed' },
    { rank: 3, name: '王五', t1: 88, t2: 72, t3: 80, t4: 76, total: 80, status: 'passed' },
    { rank: 4, name: '赵六', t1: 65, t2: 70, t3: 68, t4: 72, total: 69, status: 'passed' },
    { rank: 5, name: '陈七', t1: 78, t2: 55, t3: 60, t4: 58, total: 63, status: 'passed' },
    { rank: 6, name: '周八', t1: 50, t2: 60, t3: 45, t4: 55, total: 53, status: 'failed' },
    { rank: 7, name: '吴九', t1: 40, t2: 48, t3: 35, t4: 42, total: 42, status: 'failed' },
    { rank: 8, name: '郑十', t1: 30, t2: 35, t3: 28, t4: 32, total: 32, status: 'failed' }
  ]

  // 如果需要处理特定 examId，可在此扩展
  const titleMap = {
    'exam-002': '数据结构与算法专题考核',
    'exam-003': 'AI 编程能力测试（5月场）'
  }

  return {
    stats: {
      totalParticipants: students.length,
      passRate: 63,
      avgScore: 64.5,
      pendingReview: 2
    },
    distribution: [
      { range: '0-10', count: 0 },
      { range: '10-20', count: 0 },
      { range: '20-30', count: 0 },
      { range: '30-40', count: 2 },
      { range: '40-50', count: 1 },
      { range: '50-60', count: 1 },
      { range: '60-70', count: 1 },
      { range: '70-80', count: 1 },
      { range: '80-90', count: 1 },
      { range: '90-100', count: 1 }
    ],
    students,
    gradingDetail: {
      student: '王五',
      question: '二叉树遍历优化',
      autoScores: {
        correctness: 35,
        performance: 18,
        style: 12,
        coverage: 15
      },
      code: `def inorder_traversal(root):
    """二叉树中序遍历 - 迭代实现"""
    result = []
    stack = []
    current = root
    while stack or current:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.val)
        current = current.right
    return result

def preorder_traversal(root):
    """二叉树前序遍历 - 迭代实现"""
    if not root:
        return []
    result = []
    stack = [root]
    while stack:
        node = stack.pop()
        result.append(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return result`,
      meta: {
        language: 'Python',
        time: '42:18',
        submits: 3,
        aiRounds: 8,
        tokens: 5200
      }
    }
  }
}
