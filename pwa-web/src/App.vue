<template>
  <n-config-provider :locale="zhCN" :theme="isDark ? darkTheme : undefined">
    <n-message-provider>
      <n-dialog-provider>
        <n-notification-provider>
          <n-layout>
            <n-layout-header style="height: 60px; padding: 0 24px; display: flex; align-items: center; border-bottom: 1px solid var(--border-color)">
              <n-space align="center" style="width: 100%">
                <n-text strong style="font-size: 20px">🤖 AI 博客助手</n-text>
                <n-space style="margin-left: auto">
                  <n-button quaternary @click="$router.push('/')">生成博客</n-button>
                  <n-button quaternary @click="$router.push('/blogs')">博客列表</n-button>
                </n-space>
              </n-space>
            </n-layout-header>
            <n-layout-content style="padding: 24px; min-height: calc(100vh - 60px)">
              <router-view />
            </n-layout-content>
          </n-layout>
        </n-notification-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { ref, computed } from 'vue'
import { zhCN, darkTheme } from 'naive-ui'
import { useOsTheme } from 'naive-ui'

const osTheme = useOsTheme()
const isDark = computed(() => osTheme.value === 'dark')
</script>

<style>
:root {
  --border-color: #f0f0f0;
}

.dark {
  --border-color: #333;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}
</style>
