import { ref } from 'vue'

export function useTTS() {
  const isPlaying = ref(false)
  const currentIndex = ref(-1)
  const words = ref<string[]>([])
  let timer: ReturnType<typeof setTimeout> | null = null

  function speak(text: string, rate: number = 1.0): Promise<void> {
    return new Promise((resolve) => {
      console.log('[TTS] 开始朗读:', text)

      // #ifdef APP-PLUS
      // App 端使用讯飞语音或系统 TTS
      try {
        // 尝试使用 plus.speech（如果模块正确加载）
        if (plus.speech && typeof plus.speech.startSpeak === 'function') {
          plus.speech.startSpeak(text, { rate }, resolve, resolve)
        } else {
          // 备用方案：使用 plus.android 调用系统 TTS
          speakWithAndroidTTS(text, rate, resolve)
        }
      } catch (e) {
        console.error('[TTS] App 朗读异常:', e)
        resolve()
      }
      // #endif

      // #ifdef H5
      // H5 端使用 Web Speech API
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

  // #ifdef APP-PLUS
  function speakWithAndroidTTS(text: string, rate: number, callback: () => void) {
    try {
      // 使用 Android 系统 TTS
      const main = plus.android.runtimeMainActivity()
      const TextToSpeech = plus.android.importClass('android.speech.tts.TextToSpeech')
      const tts = new TextToSpeech(main, null)

      // 设置语速
      tts.setSpeechRate(rate)

      // 开始朗读
      tts.speak(text, TextToSpeech.QUEUE_FLUSH, null)

      // 监听朗读完成
      setTimeout(callback, text.length * 500 / rate)
    } catch (e) {
      console.error('[TTS] Android TTS 失败:', e)
      callback()
    }
  }
  // #endif

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
    try {
      if (plus.speech && typeof plus.speech.stopSpeak === 'function') {
        plus.speech.stopSpeak()
      }
    } catch (e) {}
    // #endif
  }

  function skipNext() {
    // #ifdef H5
    speechSynthesis.cancel()
    // #endif
  }

  return { isPlaying, currentIndex, words, setWords, playSequence, stop, skipNext }
}
