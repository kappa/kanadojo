let currentAudio: HTMLAudioElement | null = null;

function play(path: string): void {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
  const audio = new Audio(path);
  currentAudio = audio;
  audio.play().catch(() => {
    // Silently fail if autoplay is blocked
  });
}

function isTeluguChar(char: string): boolean {
  const code = char.codePointAt(0) ?? 0;
  return code >= 0x0c00 && code <= 0x0c7f;
}

function speakWithSynthesis(text: string, lang: string): void {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = 0.85;
  window.speechSynthesis.speak(utterance);
}

export function speakChar(char: string, romaji?: string): void {
  if (isTeluguChar(char)) {
    speakWithSynthesis(char, "te-IN");
    return;
  }
  if (romaji) {
    play(`${import.meta.env.BASE_URL}audio/char-${romaji}.mp3`);
  }
}

export function speakWord(
  text: string,
  type?: "hiragana" | "katakana" | "telugu",
): void {
  if (type === "telugu") {
    speakWithSynthesis(text, "te-IN");
    return;
  }
  const prefix = type === "katakana" ? "k-" : "";
  play(`${import.meta.env.BASE_URL}audio/word-${prefix}${text}.mp3`);
}
