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
</style>
