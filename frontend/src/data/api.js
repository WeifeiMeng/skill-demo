/**
 * api.js — API 包装层，自动降级为 Mock 数据。
 * 当后端服务不可用时，所有请求回退到本地 mockData 工厂函数。
 */
import {
  getChallenges,
  getUserProfile,
  getUserActivities,
  getScoreReport,
  getSolutions,
  getContestData,
  getLeaderboard,
  getRatingTrend,
  getExamSessions,
  getExamStats,
  getMonitorData,
  getGradingData
} from './mockData.js'

const API_BASE = 'http://localhost:8000'

/**
 * 通用请求封装：先尝试真实 API，失败或被拒绝则回退到 mockFn。
 * @param {string} url       请求 URL
 * @param {object} options   fetch 选项
 * @param {function|*} mockFn  回退数据（函数或静态值）
 * @returns {Promise<any>}
 */
async function fetchOrMock(url, options, mockFn) {
  try {
    const res = await fetch(url, options)
    if (res.ok) return res.json()
  } catch (_) {
    // 网络错误等，静默降级
  }
  return typeof mockFn === 'function' ? mockFn() : mockFn
}

// ---------------------------------------------------------------------------
// 导出的 API 函数（按 mockData 工厂函数一一对应）
// ---------------------------------------------------------------------------

/** 获取挑战列表 */
export async function fetchChallenges() {
  return fetchOrMock(`${API_BASE}/challenges`, {}, getChallenges)
}

/** 获取用户信息 */
export async function fetchUserProfile() {
  return fetchOrMock(`${API_BASE}/user/profile`, {}, getUserProfile)
}

/** 获取用户动态 */
export async function fetchUserActivities() {
  return fetchOrMock(`${API_BASE}/user/activities`, {}, getUserActivities)
}

/** 获取成绩报告 */
export async function fetchScoreReport(filename) {
  return fetchOrMock(`${API_BASE}/scores/${filename}`, {}, () => getScoreReport(filename))
}

/** 获取题解列表 */
export async function fetchSolutions() {
  return fetchOrMock(`${API_BASE}/solutions`, {}, getSolutions)
}

/** 获取竞赛数据 */
export async function fetchContestData() {
  return fetchOrMock(`${API_BASE}/contest`, {}, getContestData)
}

/** 获取排行榜 */
export async function fetchLeaderboard() {
  return fetchOrMock(`${API_BASE}/leaderboard`, {}, getLeaderboard)
}

/** 获取 Rating 趋势 */
export async function fetchRatingTrend() {
  return fetchOrMock(`${API_BASE}/user/rating-trend`, {}, getRatingTrend)
}

/** 获取考试场次列表 */
export async function fetchExamSessions() {
  return fetchOrMock(`${API_BASE}/exams`, {}, getExamSessions)
}

/** 获取考试统计摘要 */
export async function fetchExamStats() {
  return fetchOrMock(`${API_BASE}/exams/stats`, {}, getExamStats)
}

/** 获取监考实时数据 */
export async function fetchMonitorData(examId) {
  return fetchOrMock(`${API_BASE}/monitor/${examId}`, {}, () => getMonitorData(examId))
}

/** 获取阅卷 / 成绩分析数据 */
export async function fetchGradingData(examId) {
  return fetchOrMock(`${API_BASE}/grading/${examId}`, {}, () => getGradingData(examId))
}
