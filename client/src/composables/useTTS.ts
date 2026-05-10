import { ref } from 'vue'

export function useTTS() {
  const isPlaying = ref(false)
  const currentIndex = ref(-1)
  const words = ref<string[]>([])
  let timer: ReturnType<typeof setTimeout> | null = null

  function speak(text: string, rate: number = 1.0): Promise<void> {
    return new Promise((resolve) => {
      // #ifdef APP-PLUS
      ;(plus.speech as any).startSpeak(text, {
        rate,
        onComplete: () => resolve(),
        onError: () => resolve(),
      })
      // #endif

      // #ifdef H5
      const utter = new SpeechSynthesisUtterance(text)
      utter.rate = rate
      utter.lang = 'zh-CN'
      utter.onend = () => resolve()
      utter.onerror = () => resolve()
      speechSynthesis.speak(utter)
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
  }

  function skipNext() {
    // #ifdef H5
    speechSynthesis.cancel()
    // #endif
  }

  return { isPlaying, currentIndex, words, setWords, playSequence, stop, skipNext }
}
