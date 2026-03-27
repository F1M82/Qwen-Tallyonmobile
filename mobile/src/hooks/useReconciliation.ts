import { useMutation, useQueryClient } from '@tanstack/react-query';
import { reconciliationAPI } from '../services/api';

interface UploadParams {
  partyId: string;
  file: {
    uri: string;
    type?: string;
    name?: string;
  };
}

export function useUploadReconciliation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ partyId, file }: UploadParams) =>
      reconciliationAPI.upload(partyId, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reconciliation'] });
    },
  });
}

export function useConfirmMatches(reconId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (matchIds: string[]) =>
      reconciliationAPI.confirm(reconId, matchIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reconciliation', reconId] });
    },
  });
}
