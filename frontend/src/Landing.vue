<template>
  <div class="landing">

    <!-- Hero -->
    <section class="hero">
      <h1 class="hero-title">AI Done</h1>
      <p class="hero-subtitle">评估和提升每个人利用 AI 技术解决问题的能力</p>
    </section>

    <!-- Dual-role cards -->
    <section class="roles">
      <div class="role-card" @click="goChallenges">
        <div class="role-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <circle cx="24" cy="16" r="8" stroke="currentColor" stroke-width="2.5"/>
            <path d="M10 40c0-7.732 6.268-14 14-14s14 6.268 14 14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
        </div>
        <h2 class="role-title">个人学习者</h2>
        <p class="role-desc">通过实战题目提升你的 AI 驱动开发能力</p>
        <span class="role-link">开始学习 &rarr;</span>
      </div>

      <div class="role-card" @click="goChallenges">
        <div class="role-icon">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
            <rect x="6" y="8" width="36" height="32" rx="4" stroke="currentColor" stroke-width="2.5"/>
            <line x1="6" y1="20" x2="42" y2="20" stroke="currentColor" stroke-width="2.5"/>
            <line x1="20" y1="20" x2="20" y2="40" stroke="currentColor" stroke-width="2.5"/>
          </svg>
        </div>
        <h2 class="role-title">企业招聘</h2>
        <p class="role-desc">用真实项目场景评估候选人的 AI 问题解决能力</p>
        <span class="role-link">创建考核 &rarr;</span>
      </div>
    </section>

    <!-- About -->
    <section class="about">
      <h2 class="about-title">AI Done 是什么？</h2>
      <p class="about-text">
        AI Done 是一个让每个人都能够使用 AI 技术完成实际项目的平台。
        无论你是想提升自己的 AI 协作能力，还是想为团队找到真正能用 AI 解决问题的人才，
        这里都能满足你的需求。
      </p>
    </section>

    <!-- Bottom CTA -->
    <section class="bottom-cta">
      <button class="cta-button" @click="goChallenges">
        点击进入 Vibe Coding Online
      </button>
    </section>

  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goChallenges = () => {
  router.push({ name: 'challenges' })
}
</script>

<style scoped>
.landing {
  max-width: 900px;
  margin: 0 auto;
  padding: 80px 32px 64px;
}

/* Hero */
.hero {
  text-align: center;
  margin-bottom: 64px;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  margin: 0 0 16px;
  background: linear-gradient(135deg, #4a6cf7 0%, #a855f7 50%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1.5px;
}

.hero-subtitle {
  font-size: 18px;
  color: #64748b;
  margin: 0;
  font-weight: 400;
  line-height: 1.6;
  max-width: 480px;
  margin-inline: auto;
}

/* Dual-role cards */
.roles {
  display: flex;
  gap: 24px;
  margin-bottom: 64px;
  justify-content: center;
}

.role-card {
  flex: 1;
  max-width: 380px;
  padding: 40px 32px;
  border-radius: 20px;
  border: 1px solid #e2e8f0;
  background: #fff;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}

.role-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(74, 108, 247, 0.12);
  border-color: #c7d2fe;
}

.role-icon {
  color: #4a6cf7;
  margin-bottom: 20px;
}

.role-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 10px;
}

.role-desc {
  font-size: 15px;
  color: #64748b;
  margin: 0 0 20px;
  line-height: 1.6;
}

.role-link {
  font-size: 15px;
  font-weight: 600;
  color: #4a6cf7;
}

.role-card:hover .role-link {
  text-decoration: underline;
}

/* About */
.about {
  text-align: center;
  margin-bottom: 64px;
  padding: 0 32px;
}

.about-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 16px;
}

.about-text {
  font-size: 16px;
  color: #64748b;
  line-height: 1.8;
  max-width: 600px;
  margin: 0 auto;
}

/* Bottom CTA */
.bottom-cta {
  text-align: center;
}

.cta-button {
  display: inline-block;
  padding: 16px 48px;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  border: none;
  border-radius: 14px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 20px rgba(74, 108, 247, 0.3);
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(74, 108, 247, 0.4);
}
</style>
