import { ref } from 'vue'
import { BASE_URL } from '@/api/config'

export function useTTS() {
  const isPlaying = ref(false)
  const currentIndex = ref(-1)
  const words = ref<string[]>([])
  let timer: ReturnType<typeof setTimeout> | null = null
  let audioContext: UniApp.InnerAudioContext | null = null

  // 默认使用云扬音色，适合听写
  const defaultVoice = 'yunxiang'

  function getTTSAudioUrl(text: string, rate: number = 1.0): string {
    // 使用后端 Edge-TTS API
    const params = new URLSearchParams({
      text,
      voice: defaultVoice,
      rate: rate.toString(),
    })
    return `${BASE_URL}/tts/speak?${params.toString()}`
  }

  function speak(text: string, rate: number = 1.0): Promise<void> {
    return new Promise((resolve) => {
      console.log('[TTS] 开始朗读:', text)

      // #ifdef APP-PLUS
      try {
        // 先销毁之前的实例
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

        audioContext.onPlay(() => {
          console.log('[TTS] 音频开始播放')
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
        console.error('[TTS] App 朗读异常:', e)
        resolve()
      }
      // #endif

      // #ifdef H5
      // H5 端使用 Web Speech API（更流畅）
      const utter = new SpeechSynthesisUtterance(text)
      utter.rate = rate
      utter.lang = 'zh-CN'
      utter.onend = () => resolve()
      utter.onerror = () => resolve()
      speechSynthesis.speak(utter)
      // #endif

      // #ifndef APP-PLUS || H5
      resolve()
      // #endif
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

    // #ifdef H5
    speechSynthesis.cancel()
    // #endif

    // #ifdef APP-PLUS
    if (audioContext) {
      audioContext.stop()
      audioContext.destroy()
      audioContext = null
    }
    // #endif
  }

  function skipNext() {
    // #ifdef H5
    speechSynthesis.cancel()
    // #endif
  }

  return { isPlaying, currentIndex, words, setWords, playSequence, stop, skipNext }
}
