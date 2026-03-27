import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import { useVoiceEntry } from '../hooks/useVoiceEntry';
import { useNavigation } from '@react-navigation/native';
import { voucherAPI } from '../services/api';

export default function VoiceEntryScreen() {
  const navigation = useNavigation();
  const [isRecording, setIsRecording] = useState(false);
  const [recording, setRecording] = useState<Audio.Recording | undefined>();
  const [transcript, setTranscript] = useState('');
  const [parsedData, setParsedData] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const mutation = useVoiceEntry();

  async function startRecording() {
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert('Permission Required', 'Microphone access is needed for voice entry');
        return;
      }

      await Audio.setAudioModeAsync({ allowsRecordingIOS: true, playsInSilentModeIOS: true });

      const { recording: rec } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY,
      );

      setRecording(rec);
      setIsRecording(true);
    } catch {
      Alert.alert('Error', 'Failed to start recording');
    }
  }

  async function stopRecording() {
    if (!recording) return;

    setIsRecording(false);
    await recording.stopAndUnloadAsync();
    const uri = recording.getURI();

    if (uri) {
      setIsProcessing(true);
      try {
        const file = { uri, type: 'audio/mp4', name: 'voice-entry.m4a' };
        const response = await mutation.mutateAsync(file);
        setTranscript(response.data.transcript);
        setParsedData(response.data.parsed);
      } catch (error: any) {
        Alert.alert('Error', error.message);
      } finally {
        setIsProcessing(false);
      }
    }

    setRecording(undefined);
  }

  async function handlePostVoucher() {
    if (!parsedData) return;

    try {
      await voucherAPI.create(parsedData.entry);
      Alert.alert('Success', 'Voucher posted to Tally successfully', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (error: any) {
      Alert.alert('Error', error.message);
    }
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="close" size={28} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Voice Entry</Text>
        <View style={{ width: 28 }} />
      </View>

      <ScrollView style={styles.content}>
        {/* Recording Button */}
        <View style={styles.recordingSection}>
          <TouchableOpacity
            style={[styles.recordButton, isRecording && styles.recordButtonActive]}
            onPress={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
          >
            <Ionicons name={isRecording ? 'stop' : 'mic'} size={40} color="#fff" />
          </TouchableOpacity>
          <Text style={styles.recordText}>{isRecording ? 'Tap to Stop' : 'Tap to Speak'}</Text>
          {isProcessing && <ActivityIndicator size="large" color="#2563EB" />}
        </View>

        {/* Transcript */}
        {transcript ? (
          <View style={styles.resultSection}>
            <Text style={styles.sectionTitle}>I Heard:</Text>
            <View style={styles.transcriptBox}>
              <Text style={styles.transcriptText}>"{transcript}"</Text>
            </View>
          </View>
        ) : null}

        {/* Parsed Entry */}
        {parsedData?.entry && (
          <View style={styles.resultSection}>
            <Text style={styles.sectionTitle}>Entry Preview:</Text>
            <View style={styles.entryCard}>
              <View style={styles.entryRow}>
                <Text style={styles.entryLabel}>Type:</Text>
                <Text style={styles.entryValue}>{parsedData.entry.voucher_type}</Text>
              </View>
              <View style={styles.entryRow}>
                <Text style={styles.entryLabel}>Party:</Text>
                <Text style={styles.entryValue}>{parsedData.entry.party?.name || 'N/A'}</Text>
              </View>
              <View style={styles.entryRow}>
                <Text style={styles.entryLabel}>Amount:</Text>
                <Text style={styles.entryValue}>₹{parsedData.entry.amount?.toLocaleString()}</Text>
              </View>
              <View style={styles.entryRow}>
                <Text style={styles.entryLabel}>Date:</Text>
                <Text style={styles.entryValue}>{parsedData.entry.date || 'Today'}</Text>
              </View>
              {parsedData.entry.narration && (
                <View style={styles.entryRow}>
                  <Text style={styles.entryLabel}>Narration:</Text>
                  <Text style={styles.entryValue}>{parsedData.entry.narration}</Text>
                </View>
              )}
            </View>
          </View>
        )}
      </ScrollView>

      {/* Action Buttons */}
      {parsedData && (
        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.editButton} onPress={() => setParsedData(null)}>
            <Ionicons name="pencil-outline" size={20} color="#2563EB" />
            <Text style={styles.editButtonText}>Edit</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.postButton} onPress={handlePostVoucher}>
            <Ionicons name="checkmark-circle" size={20} color="#fff" />
            <Text style={styles.postButtonText}>Post to Tally</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  title: { fontSize: 20, fontWeight: '600', color: '#111827' },
  content: { flex: 1, padding: 20 },
  recordingSection: { alignItems: 'center', padding: 40 },
  recordButton: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#EF4444',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  recordButtonActive: { backgroundColor: '#DC2626' },
  recordText: { fontSize: 16, color: '#6B7280' },
  resultSection: { marginTop: 24 },
  sectionTitle: { fontSize: 16, fontWeight: '600', color: '#111827', marginBottom: 12 },
  transcriptBox: { backgroundColor: '#F3F4F6', padding: 16, borderRadius: 12, marginBottom: 16 },
  transcriptText: { fontSize: 15, color: '#374151', fontStyle: 'italic' },
  entryCard: {
    backgroundColor: '#F9FAFB',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    gap: 12,
  },
  entryRow: { flexDirection: 'row', justifyContent: 'space-between' },
  entryLabel: { fontSize: 14, color: '#6B7280' },
  entryValue: { fontSize: 14, fontWeight: '600', color: '#111827' },
  actionButtons: {
    flexDirection: 'row',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    gap: 12,
  },
  editButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 14,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2563EB',
    gap: 8,
  },
  editButtonText: { fontSize: 16, fontWeight: '600', color: '#2563EB' },
  postButton: {
    flex: 2,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 14,
    borderRadius: 8,
    backgroundColor: '#2563EB',
    gap: 8,
  },
  postButtonText: { fontSize: 16, fontWeight: '600', color: '#fff' },
});
