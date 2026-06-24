<template>
  <div class="landing">

    <!-- Minimal Header -->
    <header class="landing-header">
      <div class="header-logo">AI Done</div>
      <div class="header-actions">
        <template v-if="loggedIn">
          <span class="header-user">{{ username }}</span>
          <button class="header-btn-outline" @click="doLogout">退出</button>
        </template>
        <template v-else>
          <button class="header-btn-outline" @click="openAuth('login')">登录</button>
          <button class="header-btn-fill" @click="openAuth('register')">注册</button>
        </template>
      </div>
    </header>

    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg"></div>
      <h1 class="hero-title">AI Done</h1>
      <p class="hero-subtitle">评估和提升每个人利用 AI 技术解决问题的能力</p>
      <p class="hero-desc">从 AI 编程到数据分析，从自动化脚本到创意生成 — 通过真实场景挑战，让你和 AI 真正协作起来</p>
      <div class="hero-buttons">
        <button class="hero-btn-primary" @click="goChallenges">立即体验</button>
        <button class="hero-btn-outline" @click="goChallenges">了解更多</button>
      </div>
    </section>

    <!-- Stats -->
    <section class="stats">
      <div class="stat-item">
        <span class="stat-number">20+</span>
        <span class="stat-label">实战场景</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-number">50+</span>
        <span class="stat-label">挑战题目</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item">
        <span class="stat-number">10,000+</span>
        <span class="stat-label">完成项目</span>
      </div>
    </section>

    <!-- Capabilities -->
    <section class="capabilities">
      <h2 class="section-title">涵盖多种 AI 协作场景</h2>
      <p class="section-sub">不只是写代码，而是用 AI 完成任何任务</p>
      <div class="cap-grid">
        <div class="cap-card">
          <div class="cap-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect x="2" y="4" width="28" height="22" rx="3" stroke="currentColor" stroke-width="2"/>
              <path d="M10 16l4 4 8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3 class="cap-title">AI 编程</h3>
          <p class="cap-desc">使用 AI 辅助完成从前端到后端的完整项目开发</p>
        </div>
        <div class="cap-card">
          <div class="cap-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect x="3" y="3" width="12" height="12" rx="2" stroke="currentColor" stroke-width="2"/>
              <rect x="17" y="3" width="12" height="12" rx="2" stroke="currentColor" stroke-width="2"/>
              <rect x="3" y="17" width="12" height="12" rx="2" stroke="currentColor" stroke-width="2"/>
              <rect x="17" y="17" width="12" height="12" rx="2" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <h3 class="cap-title">数据分析</h3>
          <p class="cap-desc">借助 AI 清洗数据、生成图表、挖掘洞察</p>
        </div>
        <div class="cap-card">
          <div class="cap-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <circle cx="16" cy="16" r="13" stroke="currentColor" stroke-width="2"/>
              <path d="M10 16a6 6 0 016-6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <circle cx="16" cy="16" r="3" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <h3 class="cap-title">自动化</h3>
          <p class="cap-desc">用 AI 设计工作流、编写脚本，让重复性事务自动运行</p>
        </div>
        <div class="cap-card">
          <div class="cap-icon">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <path d="M16 2l4 8 9 1.5-6.5 6 1.5 9L16 23l-8 3.5 1.5-9L3 11.5l9-1.5z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3 class="cap-title">创意生成</h3>
          <p class="cap-desc">利用 AI 进行文案创作、方案策划、产品设计等创意工作</p>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="how-it-works">
      <h2 class="section-title">三步入门</h2>
      <p class="section-sub">从选择挑战到获得反馈，全流程在线完成</p>
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <h3 class="step-title">选择挑战</h3>
          <p class="step-desc">从我们的实战题库中选择你想要挑战的场景，覆盖开发、数据、自动化等多个领域</p>
        </div>
        <div class="step-arrow">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
            <path d="M12 20h16M22 14l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <h3 class="step-title">AI 协作解决</h3>
          <p class="step-desc">在在线环境中，与 AI 助手实时协作，动手完成完整的项目任务</p>
        </div>
        <div class="step-arrow">
          <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
            <path d="M12 20h16M22 14l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <h3 class="step-title">获得评估反馈</h3>
          <p class="step-desc">系统自动评估你的完成质量，企业可以通过评估报告了解候选人的真实 AI 协作水平</p>
        </div>
      </div>
    </section>

    <!-- Dual Scenarios -->
    <section class="scenarios">
      <h2 class="section-title">为你而设计</h2>
      <p class="section-sub">无论你是想提升自己，还是寻找人才，AI Done 都能满足你</p>
      <div class="scenario-cards">
        <div class="scenario-card individual" @click="goChallenges">
          <div class="scenario-badge">个人版</div>
          <div class="scenario-icon">
            <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
              <circle cx="28" cy="18" r="10" stroke="currentColor" stroke-width="2.5"/>
              <path d="M10 48c0-9.941 8.059-18 18-18s18 8.059 18 18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
            </svg>
          </div>
          <h3 class="scenario-title">个人学习者</h3>
          <ul class="scenario-features">
            <li>覆盖多个领域的实战挑战题目</li>
            <li>在线 IDE + AI 助手，随时开始练习</li>
            <li>实时自动评分，了解自己的能力水平</li>
            <li>追踪进步轨迹，看到自己的成长</li>
          </ul>
          <span class="scenario-cta">开始学习 &rarr;</span>
        </div>

        <div class="scenario-card enterprise" @click="goAdmin">
          <div class="scenario-badge">企业版</div>
          <div class="scenario-icon">
            <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
              <rect x="6" y="8" width="44" height="40" rx="5" stroke="currentColor" stroke-width="2.5"/>
              <line x1="6" y1="24" x2="50" y2="24" stroke="currentColor" stroke-width="2.5"/>
              <line x1="24" y1="24" x2="24" y2="48" stroke="currentColor" stroke-width="2.5"/>
            </svg>
          </div>
          <h3 class="scenario-title">企业招聘</h3>
          <ul class="scenario-features">
            <li>用真实项目场景评估候选人，而非算法题</li>
            <li>观察候选人如何与 AI 协作解决实际问题</li>
            <li>自动生成评估报告，量化 AI 协作能力</li>
            <li>支持自定义考核场景，匹配岗位需求</li>
          </ul>
          <span class="scenario-cta">创建考核 &rarr;</span>
        </div>
      </div>
    </section>

    <!-- Bottom CTA -->
    <section class="bottom-cta">
      <h2 class="cta-title">准备好开始了吗？</h2>
      <p class="cta-sub">加入我们，体验新时代的 AI 协作工作方式</p>
      <button class="cta-button" @click="goChallenges">
        点击进入 Vibe Coding Online
      </button>
    </section>

    <!-- Footer -->
    <footer class="landing-footer">
      <span class="footer-brand">AI Done</span>
      <span class="footer-copy">评估和提升每个人利用 AI 技术解决问题的能力</span>
    </footer>

  </div>
</template>

<script setup>
import { inject } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Inject auth state and actions from App.vue
const openAuth = inject('openAuth', () => {})
const loggedIn = inject('authLoggedIn', false)
const username = inject('authUsername', '')
const doLogout = inject('doLogout', () => {})

const goChallenges = () => {
  router.push({ name: 'challenges' })
}

const goAdmin = () => {
  router.push({ name: 'adminDashboard' })
}
</script>

<style scoped>
/* ===== Base ===== */
.landing {
  min-height: 100vh;
  background: #fafbff;
  overflow-x: hidden;
}

/* ===== Header ===== */
.landing-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 48px;
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(250, 251, 255, 0.8);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.header-logo {
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(135deg, #4a6cf7, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-user {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
}

.header-btn-outline {
  padding: 7px 20px;
  background: transparent;
  border: 1px solid #c7d2fe;
  color: #4a6cf7;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}
.header-btn-outline:hover {
  background: rgba(74, 108, 247, 0.06);
}

.header-btn-fill {
  padding: 7px 20px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
}
.header-btn-fill:hover {
  opacity: 0.9;
}

/* ===== Hero ===== */
.hero {
  position: relative;
  text-align: center;
  padding: 100px 32px 80px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 60% at 50% 0%, rgba(74, 108, 247, 0.08), transparent),
    radial-gradient(ellipse 60% 50% at 80% 80%, rgba(168, 85, 247, 0.06), transparent),
    radial-gradient(ellipse 50% 50% at 20% 70%, rgba(236, 72, 153, 0.04), transparent);
  pointer-events: none;
}

.hero-title {
  position: relative;
  font-size: 64px;
  font-weight: 800;
  margin: 0 0 20px;
  background: linear-gradient(135deg, #4a6cf7 0%, #a855f7 40%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -2px;
}

.hero-subtitle {
  position: relative;
  font-size: 20px;
  color: #334155;
  margin: 0 0 12px;
  font-weight: 600;
}

.hero-desc {
  position: relative;
  font-size: 16px;
  color: #64748b;
  max-width: 540px;
  margin: 0 auto 36px;
  line-height: 1.7;
}

.hero-buttons {
  position: relative;
  display: flex;
  gap: 16px;
  justify-content: center;
}

.hero-btn-primary {
  padding: 14px 40px;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 20px rgba(74, 108, 247, 0.3);
}
.hero-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(74, 108, 247, 0.4);
}

.hero-btn-outline {
  padding: 14px 40px;
  font-size: 16px;
  font-weight: 600;
  color: #4a6cf7;
  background: transparent;
  border: 1.5px solid #c7d2fe;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.hero-btn-outline:hover {
  background: rgba(74, 108, 247, 0.04);
}

/* ===== Stats ===== */
.stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  padding: 48px 32px;
  max-width: 700px;
  margin: 0 auto;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 500;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: #e2e8f0;
}

/* ===== Section titles ===== */
.section-title {
  text-align: center;
  font-size: 30px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px;
}

.section-sub {
  text-align: center;
  font-size: 16px;
  color: #64748b;
  margin: 0 0 48px;
}

/* ===== Capabilities ===== */
.capabilities {
  padding: 80px 32px;
  max-width: 1000px;
  margin: 0 auto;
}

.cap-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.cap-card {
  padding: 32px 24px;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #f1f5f9;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}
.cap-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
}

.cap-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(74, 108, 247, 0.1), rgba(168, 85, 247, 0.1));
  color: #4a6cf7;
  margin-bottom: 16px;
}

.cap-title {
  font-size: 17px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.cap-desc {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

/* ===== How It Works ===== */
.how-it-works {
  padding: 80px 32px;
  max-width: 1000px;
  margin: 0 auto;
}

.steps {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 20px;
}

.step {
  flex: 1;
  text-align: center;
  max-width: 280px;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  font-size: 18px;
  font-weight: 800;
  margin-bottom: 16px;
}

.step-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.step-desc {
  font-size: 14px;
  color: #64748b;
  line-height: 1.7;
  margin: 0;
}

.step-arrow {
  display: flex;
  align-items: flex-start;
  padding-top: 8px;
  color: #cbd5e1;
  flex-shrink: 0;
}

/* ===== Scenarios ===== */
.scenarios {
  padding: 80px 32px;
  max-width: 1000px;
  margin: 0 auto;
}

.scenario-cards {
  display: flex;
  gap: 32px;
  justify-content: center;
}

.scenario-card {
  flex: 1;
  max-width: 440px;
  padding: 48px 36px;
  border-radius: 24px;
  background: #fff;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  position: relative;
  overflow: hidden;
}
.scenario-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(74, 108, 247, 0.1);
  border-color: #c7d2fe;
}

.scenario-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
}
.individual .scenario-badge {
  background: rgba(74, 108, 247, 0.1);
  color: #4a6cf7;
}
.enterprise .scenario-badge {
  background: rgba(168, 85, 247, 0.1);
  color: #a855f7;
}

.scenario-icon {
  color: #4a6cf7;
  margin-bottom: 20px;
}
.enterprise .scenario-icon {
  color: #a855f7;
}

.scenario-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 20px;
}

.scenario-features {
  list-style: none;
  padding: 0;
  margin: 0 0 28px;
}

.scenario-features li {
  position: relative;
  padding-left: 20px;
  font-size: 14px;
  color: #475569;
  line-height: 2;
}
.scenario-features li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 11px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4a6cf7;
}
.enterprise .scenario-features li::before {
  background: #a855f7;
}

.scenario-cta {
  font-size: 16px;
  font-weight: 700;
  color: #4a6cf7;
}
.enterprise .scenario-cta {
  color: #a855f7;
}
.scenario-card:hover .scenario-cta {
  text-decoration: underline;
}

/* ===== Bottom CTA ===== */
.bottom-cta {
  text-align: center;
  padding: 80px 32px;
  background: linear-gradient(135deg, rgba(74, 108, 247, 0.04), rgba(168, 85, 247, 0.04));
}

.cta-title {
  font-size: 30px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px;
}

.cta-sub {
  font-size: 16px;
  color: #64748b;
  margin: 0 0 32px;
}

.cta-button {
  display: inline-block;
  padding: 18px 56px;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  border: none;
  border-radius: 14px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 24px rgba(74, 108, 247, 0.3);
}
.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(74, 108, 247, 0.4);
}

/* ===== Footer ===== */
.landing-footer {
  text-align: center;
  padding: 40px 32px;
  border-top: 1px solid #f1f5f9;
}

.footer-brand {
  display: block;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #4a6cf7, #a855f7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.footer-copy {
  font-size: 13px;
  color: #94a3b8;
}
</style>
