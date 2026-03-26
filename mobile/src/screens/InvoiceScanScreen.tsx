import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { useInvoiceScan } from '../hooks/useInvoiceScan';
import { useNavigation } from '@react-navigation/native';
import { voucherAPI } from '../services/api';

export default function InvoiceScanScreen() {
  const navigation = useNavigation();
  const [image, setImage] = useState<string | null>(null);
  const [scannedData, setScannedData] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const mutation = useInvoiceScan();

  async function pickImage() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (permission.status !== 'granted') {
      Alert.alert('Permission Required', 'Camera roll access is needed');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [3, 4],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setImage(result.assets[0].uri);
      await scanInvoice(result.assets[0].uri);
    }
  }

  async function takePhoto() {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (permission.status !== 'granted') {
      Alert.alert('Permission Required', 'Camera access is needed');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [3, 4],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setImage(result.assets[0].uri);
      await scanInvoice(result.assets[0].uri);
    }
  }

  async function scanInvoice(uri: string) {
    setIsProcessing(true);
    try {
      const file = {
        uri,
        type: 'image/jpeg',
        name: 'invoice.jpg',
      };

      const response = await mutation.mutateAsync(file);
      setScannedData(response.data);
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setIsProcessing(false);
    }
  }

  async function handlePostVoucher() {
    if (!scannedData) return;

    try {
      await voucherAPI.create({
        voucher_type: scannedData.voucher_type === 'Sales Invoice' ? 'Sales' : 'Purchase',
        date: scannedData.invoice_date,
        party_name: scannedData.supplier?.name || scannedData.buyer?.name,
        amount: scannedData.totals?.grand_total,
        reference_number: scannedData.invoice_number,
        gst_details: scannedData.totals,
      });
      Alert.alert('Success', 'Invoice posted to Tally successfully', [
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
        <Text style={styles.title}>Scan Invoice</Text>
        <View style={{ width: 28 }} />
      </View>

      <ScrollView style={styles.content}>
        {!image ? (
          <View style={styles.placeholder}>
            <Ionicons name="image-outline" size={80} color="#D1D5DB" />
            <Text style={styles.placeholderText}>No image selected</Text>
            <Text style={styles.placeholderSubtext}>
              Take a photo or choose from your library
            </Text>
          </View>
        ) : (
          <View style={styles.imageContainer}>
            <Image source={{ uri: image }} style={styles.invoiceImage} />
            <TouchableOpacity
              style={styles.retakeButton}
              onPress={() => {
                setImage(null);
                setScannedData(null);
              }}
            >
              <Ionicons name="refresh" size={20} color="#fff" />
              <Text style={styles.retakeButtonText}>Retake</Text>
            </TouchableOpacity>
          </View>
        )}

        {isProcessing && (
          <View style={styles.processing}>
            <ActivityIndicator size="large" color="#2563EB" />
            <Text style={styles.processingText}>Extracting invoice data...</Text>
          </View>
        )}

        {scannedData && (
          <View style={styles.resultSection}>
            <View style={styles.confidenceBadge}>
              <Ionicons
                name={
                  scannedData.confidence === 'high'
                    ? 'checkmark-circle'
                    : scannedData.confidence === 'medium'
                    ? 'warning'
                    : 'close-circle'
                }
                size={16}
                color={
                  scannedData.confidence === 'high'
                    ? '#10B981'
                    : scannedData.confidence === 'medium'
                    ? '#F59E0B'
                    : '#EF4444'
                }
              />
              <Text
                style={[
                  styles.confidenceText,
                  {
                    color:
                      scannedData.confidence === 'high'
                        ? '#10B981'
                        : scannedData.confidence === 'medium'
                        ? '#F59E0B'
                        : '#EF4444',
                  },
                ]}
              >
                {scannedData.confidence.toUpperCase()} CONFIDENCE
              </Text>
            </View>

            <View style={styles.infoCard}>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Type:</Text>
                <Text style={styles.infoValue}>{scannedData.voucher_type}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Invoice No:</Text>
                <Text style={styles.infoValue}>{scannedData.invoice_number}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Date:</Text>
                <Text style={styles.infoValue}>{scannedData.invoice_date}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Party:</Text>
                <Text style={styles.infoValue}>
                  {scannedData.supplier?.name || scannedData.buyer?.name}
                </Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>GSTIN:</Text>
                <Text style={styles.infoValue}>
                  {scannedData.supplier?.gstin || scannedData.buyer?.gstin}
                </Text>
              </View>
            </View>

            <View style={styles.totalsCard}>
              <Text style={styles.totalsTitle}>Totals</Text>
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>Taxable Value:</Text>
                <Text style={styles.totalValue}>
                  ₹{scannedData.totals?.taxable_value?.toLocaleString()}
                </Text>
              </View>
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>CGST:</Text>
                <Text style={styles.totalValue}>
                  ₹{scannedData.totals?.cgst?.toLocaleString()}
                </Text>
              </View>
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>SGST:</Text>
                <Text style={styles.totalValue}>
                  ₹{scannedData.totals?.sgst?.toLocaleString()}
                </Text>
              </View>
              <View style={styles.totalRow}>
                <Text style={styles.totalLabel}>IGST:</Text>
                <Text style={styles.totalValue}>
                  ₹{scannedData.totals?.igst?.toLocaleString()}
                </Text>
              </View>
              <View style={[styles.totalRow, styles.grandTotalRow]}>
                <Text style={styles.grandTotalLabel}>Grand Total:</Text>
                <Text style={styles.grandTotalValue}>
                  ₹{scannedData.totals?.grand_total?.toLocaleString()}
                </Text>
              </View>
            </View>
          </View>
        )}
      </ScrollView>

      {image && !isProcessing && (
        <View style={styles.actionButtons}>
          <TouchableOpacity
            style={styles.pickButton}
            onPress={pickImage}
          >
            <Ionicons name="images-outline" size={20} color="#2563EB" />
            <Text style={styles.pickButtonText}>Choose</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.cameraButton}
            onPress={takePhoto}
          >
            <Ionicons name="camera-outline" size={20} color="#fff" />
            <Text style={styles.cameraButtonText}>Camera</Text>
          </TouchableOpacity>
          {scannedData && (
            <TouchableOpacity
              style={styles.postButton}
              onPress={handlePostVoucher}
            >
              <Ionicons name="checkmark-circle" size={20} color="#fff" />
              <Text style={styles.postButtonText}>Post to Tally</Text>
            </TouchableOpacity>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  placeholder: {
    alignItems: 'center',
    padding: 60,
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderStyle: 'dashed',
  },
  placeholderText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 16,
  },
  placeholderSubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8,
  },
  imageContainer: {
    position: 'relative',
    borderRadius: 12,
    overflow: 'hidden',
  },
  invoiceImage: {
    width: '100%',
    height: 400,
    resizeMode: 'cover',
  },
  retakeButton: {
    position: 'absolute',
    bottom: 12,
    right: 12,
    flexDirection: 'row',
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 10,
    borderRadius: 8,
    gap: 6,
  },
  retakeButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  processing: {
    alignItems: 'center',
    padding: 40,
  },
  processingText: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 12,
  },
  resultSection: {
    marginTop: 24,
    gap: 16,
  },
  confidenceBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: '#F3F4F6',
    padding: 8,
    borderRadius: 6,
    gap: 6,
  },
  confidenceText: {
    fontSize: 12,
    fontWeight: '600',
  },
  infoCard: {
    backgroundColor: '#F9FAFB',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    gap: 12,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  infoLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  totalsCard: {
    backgroundColor: '#F9FAFB',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  totalsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  totalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  totalLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  totalValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  grandTotalRow: {
    borderBottomWidth: 0,
    marginTop: 8,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#D1D5DB',
  },
  grandTotalLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  grandTotalValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2563EB',
  },
  actionButtons: {
    flexDirection: 'row',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    gap: 12,
  },
  pickButton: {
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
  pickButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2563EB',
  },
  cameraButton: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 14,
    borderRadius: 8,
    backgroundColor: '#2563EB',
    gap: 8,
  },
  cameraButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  postButton: {
    flex: 2,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 14,
    borderRadius: 8,
    backgroundColor: '#10B981',
    gap: 8,
  },
  postButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
});
