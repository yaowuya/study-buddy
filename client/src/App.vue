<script setup lang="ts">
import { onLaunch } from '@dcloudio/uni-app'

onLaunch(() => {
  // 登录状态检查已移至登录页 onMounted 中处理
})
</script>

<style lang="scss">
@use './static/styles/variables.scss' as *;

page {
  font-family: $font-family;
  background-color: $color-surface;
  color: $color-on-surface;
}

// scroll-view 内容区顶部留白
.uni-scroll-view-content {
  padding-top: 20px;
}
</style>
