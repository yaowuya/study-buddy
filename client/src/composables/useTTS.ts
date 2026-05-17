import { ref } from 'vue'
import { BASE_URL } from '@/api/config'

export function useTTS() {
  const isPlaying = ref(false)
  const currentIndex = ref(-1)
  const words = ref<string[]>([])
  let timer: ReturnType<typeof setTimeout> | null = null
  let audioContext: UniApp.InnerAudioContext | null = null

  // 默认使用度逍遥音色
  const defaultVoice = 'xiaoyao'

  function getTTSAudioUrl(text: string, rate: number = 1.0): string {
    return `${BASE_URL}/tts/speak?text=${encodeURIComponent(text)}&voice=${defaultVoice}&rate=${rate}`
  }

  function speak(text: string, rate: number = 1.0): Promise<void> {
    return new Promise((resolve) => {
      console.log('[TTS] 开始朗读:', text)

      try {
        if (audioContext) {
          audioContext.destroy()
        }

        audioContext = uni.createInnerAudioContext()
        audioContext.volume = 1.0
        audioContext.src = getTTSAudioUrl(text, rate)

        let resolved = false
        const doResolve = () => {
          if (!resolved) {
            resolved = true
            resolve()
          }
        }

        audioContext.onCanplay(() => {
          console.log('[TTS] 音频可播放')
          audioContext?.play()
        })

        audioContext.onEnded(() => {
          console.log('[TTS] 朗读完成')
          audioContext?.destroy()
          audioContext = null
          doResolve()
        })

        audioContext.onError((e) => {
          console.error('[TTS] 播放失败:', e)
          audioContext?.destroy()
          audioContext = null
          doResolve()
        })
      } catch (e) {
        console.error('[TTS] 朗读异常:', e)
        resolve()
      }
    })
  }

  function setWords(list: string[]) {
    words.value = list
    currentIndex.value = -1
  }

  async function playSequence(rate: number = 1.0, pauseSeconds: number = 3) {
    isPlaying.value = true
    for (let i = 0; i < words.value.length; i++) {
      if (!isPlaying.value) break
      currentIndex.value = i
      await speak(words.value[i], rate)
      if (!isPlaying.value) break
      if (i < words.value.length - 1) {
        await delay(pauseSeconds * 1000)
      }
    }
    isPlaying.value = false
    currentIndex.value = -1
  }

  function delay(ms: number): Promise<void> {
    return new Promise(r => { timer = setTimeout(r, ms) })
  }

  function stop() {
    isPlaying.value = false
    currentIndex.value = -1
    if (timer) { clearTimeout(timer); timer = null }

    if (audioContext) {
      audioContext.stop()
      audioContext.destroy()
      audioContext = null
    }
  }

  return { isPlaying, currentIndex, words, setWords, playSequence, speak, stop }
}
