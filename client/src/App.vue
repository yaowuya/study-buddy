<script setup lang="ts">
import { onLaunch } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'

onLaunch(async () => {
  const authStore = useAuthStore()
  await authStore.init()
})
</script>

<style lang="scss">
@import './static/styles/variables.scss';

page {
  font-family: $font-family;
  background-color: $color-surface;
  color: $color-on-surface;
}
</style>
