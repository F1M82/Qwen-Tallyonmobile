import { useMutation } from '@tanstack/react-query';
import { voiceAPI } from '../services/api';

interface AudioFile {
  uri: string;
  type?: string;
  name?: string;
}

export function useVoiceEntry() {
  return useMutation({
    mutationFn: (audio: AudioFile) => voiceAPI.entry(audio),
  });
}
