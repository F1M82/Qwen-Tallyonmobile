import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as DocumentPicker from 'expo-document-picker';
import { useUploadReconciliation } from '../hooks/useReconciliation';
import { useNavigation } from '@react-navigation/native';
import { partyAPI } from '../services/api';

export default function ReconciliationScreen() {
  const navigation = useNavigation();
  const [selectedParty, setSelectedParty] = useState<any>(null);
  const [reconResult, setReconResult] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);
  
  const uploadMutation = useUploadReconciliation();

  async function pickDocument() {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'],
        copyToCacheDirectory: true,
      });

      if (!result.canceled && result.assets[0]) {
        if (!selectedParty) {
          Alert.alert('Select Party', 'Please select a party first');
          return;
        }

        setIsUploading(true);
        try {
          const file = {
            uri: result.assets[0].uri,
            type: result.assets[0].mimeType,
            name: result.assets[0].name,
          };

          const response = await uploadMutation.mutateAsync({
            partyId: selectedParty.id,
            file,
          });

          setReconResult(response.data);
        } catch (error: any) {
          Alert.alert('Error', error.message);
        } finally {
          setIsUploading(false);
        }
      }
    } catch (error: any) {
      Alert.alert('Error', 'Failed to pick document');
    }
  }

  async function handleConfirmMatches() {
    if (!reconResult) return;

    const matchIds = reconResult.results
      .filter((r: any) => r.auto_postable || r.status === 'exact')
      .map((r: any) => r.id);

    if (matchIds.length === 0) {
      Alert.alert('No Matches', 'No matches to confirm');
      return;
    }

    try {
      await reconciliationAPI.confirm(reconResult.recon_id, matchIds);
      Alert.alert('Success', `${matchIds.length} matches posted to Tally`, [
        { text: 'OK', onPress: () => setReconResult(null) },
      ]);
    } catch (error: any) {
      Alert.alert('Error', error.message);
    }
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Reconciliation</Text>
        <TouchableOpacity
          style={styles.historyButton}
          onPress={() => navigation.navigate('AuditTrail')}
        >
          <Ionicons name="time-outline" size={24} color="#2563EB" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* Party Selection */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Select Party</Text>
          <TouchableOpacity
            style={styles.partySelector}
            onPress={() => navigation.navigate('PartyList', { onSelect: setSelectedParty })}
          >
            <Text style={styles.partySelectorText}>
              {selectedParty?.name || 'Choose a party...'}
            </Text>
            <Ionicons name="chevron-down" size={20} color="#6B7280" />
          </TouchableOpacity>
        </View>

        {/* Upload Button */}
        {selectedParty && !reconResult && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Upload Party Statement</Text>
            <TouchableOpacity
              style={styles.uploadButton}
              onPress={pickDocument}
              disabled={isUploading}
            >
              {isUploading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <Ionicons name="cloud-upload-outline" size={24} color="#fff" />
                  <Text style={styles.uploadButtonText}>Upload PDF / Excel</Text>
                </>
              )}
            </TouchableOpacity>
            <Text style={styles.uploadHint}>
              Supports PDF, Excel, CSV from any party
            </Text>
          </View>
        )}

        {/* Results */}
        {reconResult && (
          <>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Reconciliation Summary</Text>
              <View style={styles.summaryGrid}>
                <View style={[styles.summaryCard, styles.matchedCard]}>
                  <Ionicons name="checkmark-circle" size={32} color="#10B981" />
                  <Text style={styles.summaryCount}>{reconResult.summary.matched_count}</Text>
                  <Text style={styles.summaryLabel}>Matched</Text>
                </View>
                <View style={[styles.summaryCard, styles.fuzzyCard]}>
                  <Ionicons name="warning" size={32} color="#F59E0B" />
                  <Text style={styles.summaryCount}>{reconResult.summary.fuzzy_count}</Text>
                  <Text style={styles.summaryLabel}>Fuzzy</Text>
                </View>
                <View style={[styles.summaryCard, styles.missingCard]}>
                  <Ionicons name="close-circle" size={32} color="#EF4444" />
                  <Text style={styles.summaryCount}>{reconResult.summary.missing_in_party_count}</Text>
                  <Text style={styles.summaryLabel}>Missing</Text>
                </View>
              </View>
            </View>

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Difference</Text>
              <View style={styles.differenceCard}>
                <Text style={styles.differenceLabel}>Your Books</Text>
                <Text style={styles.differenceValue}>
                  ₹{reconResult.summary.your_balance}
                </Text>
                <Text style={styles.differenceLabel}>Party Books</Text>
                <Text style={styles.differenceValue}>
                  ₹{reconResult.summary.party_balance}
                </Text>
                <View style={styles.differenceDivider} />
                <Text style={styles.differenceLabel}>Difference</Text>
                <Text
                  style={[
                    styles.differenceValue,
                    styles.differenceTotal,
                    {
                      color:
                        parseFloat(reconResult.summary.difference) === 0
                          ? '#10B981'
                          : '#EF4444',
                    },
                  ]}
                >
                  ₹{reconResult.summary.difference}
                </Text>
              </View>
            </View>

            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Actions</Text>
              <View style={styles.actionButtons}>
                <TouchableOpacity
                  style={styles.actionButton}
                  onPress={handleConfirmMatches}
                >
                  <Ionicons name="checkmark-circle-outline" size={20} color="#2563EB" />
                  <Text style={styles.actionButtonText}>Confirm Matches</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.actionButton, styles.queryButton]}
                  onPress={() => {}}
                >
                  <Ionicons name="chatbubble-outline" size={20} color="#F59E0B" />
                  <Text style={[styles.actionButtonText, styles.queryButtonText]}>
                    Query Party
                  </Text>
                </TouchableOpacity>
              </View>
              <TouchableOpacity
                style={styles.certificateButton}
                onPress={() => {}}
              >
                <Ionicons name="document-text-outline" size={20} color="#6B7280" />
                <Text style={styles.certificateButtonText}>Generate Certificate</Text>
              </TouchableOpacity>
            </View>
          </>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
  },
  historyButton: {
    padding: 8,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  partySelector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  partySelectorText: {
    fontSize: 16,
    color: '#111827',
  },
  uploadButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#2563EB',
    padding: 16,
    borderRadius: 12,
    gap: 12,
  },
  uploadButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  uploadHint: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
  },
  summaryGrid: {
    flexDirection: 'row',
    gap: 12,
  },
  summaryCard: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  matchedCard: {
    borderColor: '#10B981',
  },
  fuzzyCard: {
    borderColor: '#F59E0B',
  },
  missingCard: {
    borderColor: '#EF4444',
  },
  summaryCount: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 8,
  },
  summaryLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  differenceCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    gap: 12,
  },
  differenceLabel: {
    fontSize: 12,
    color: '#6B7280',
  },
  differenceValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
  },
  differenceDivider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginVertical: 8,
  },
  differenceTotal: {
    fontSize: 24,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 14,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#2563EB',
    gap: 8,
    backgroundColor: '#fff',
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2563EB',
  },
  queryButton: {
    borderColor: '#F59E0B',
  },
  queryButtonText: {
    color: '#F59E0B',
  },
  certificateButton: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 14,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    gap: 8,
    backgroundColor: '#fff',
    marginTop: 12,
  },
  certificateButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
  },
});
