import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import { useAuth } from '../context/AuthContext';

export default function SettingsScreen() {
  const navigation = useNavigation();
  const { user, logout } = useAuth();

  async function handleLogout() {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Logout', style: 'destructive', onPress: logout },
    ]);
  }

  const sections = [
    {
      title: 'Account',
      items: [
        { icon: 'person-outline', label: 'Profile', onPress: () => {} },
        { icon: 'business-outline', label: 'Company Settings', onPress: () => {} },
        { icon: 'shield-outline', label: 'Security', onPress: () => {} },
      ],
    },
    {
      title: 'TaxMind',
      items: [
        { icon: 'hardware-chip-outline', label: 'AI Assistant', onPress: () => {} },
        { icon: 'notifications-outline', label: 'Notifications', onPress: () => {} },
        { icon: 'wifi-outline', label: 'Tally Connection', onPress: () => {} },
      ],
    },
    {
      title: 'App',
      items: [
        { icon: 'help-circle-outline', label: 'Help & Support', onPress: () => {} },
        { icon: 'information-circle-outline', label: 'About', onPress: () => {} },
        { icon: 'log-out-outline', label: 'Logout', onPress: handleLogout, danger: true },
      ],
    },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Settings</Text>
        <View style={styles.profileCard}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{user?.full_name?.charAt(0) || 'U'}</Text>
          </View>
          <View>
            <Text style={styles.profileName}>{user?.full_name}</Text>
            <Text style={styles.profileEmail}>{user?.email}</Text>
            {user?.firm_name && <Text style={styles.profileFirm}>{user.firm_name}</Text>}
          </View>
        </View>
      </View>

      {sections.map((section) => (
        <View key={section.title} style={styles.section}>
          <Text style={styles.sectionTitle}>{section.title}</Text>
          <View style={styles.sectionCard}>
            {section.items.map((item, index) => (
              <TouchableOpacity
                key={item.label}
                style={[styles.item, index < section.items.length - 1 && styles.itemBorder]}
                onPress={item.onPress}
              >
                <Ionicons name={item.icon as any} size={20} color={item.danger ? '#EF4444' : '#374151'} />
                <Text style={[styles.itemLabel, item.danger && styles.dangerLabel]}>{item.label}</Text>
                <Ionicons name="chevron-forward" size={16} color="#9CA3AF" />
              </TouchableOpacity>
            ))}
          </View>
        </View>
      ))}
      <Text style={styles.version}>TaxMind v1.0.0</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { backgroundColor: '#fff', padding: 20, paddingTop: 60, borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 24, fontWeight: 'bold', color: '#111827', marginBottom: 16 },
  profileCard: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  avatar: { width: 56, height: 56, borderRadius: 28, backgroundColor: '#2563EB', justifyContent: 'center', alignItems: 'center' },
  avatarText: { color: '#fff', fontSize: 22, fontWeight: 'bold' },
  profileName: { fontSize: 16, fontWeight: '600', color: '#111827' },
  profileEmail: { fontSize: 14, color: '#6B7280' },
  profileFirm: { fontSize: 12, color: '#2563EB', marginTop: 2 },
  section: { padding: 20, paddingBottom: 0 },
  sectionTitle: { fontSize: 12, fontWeight: '600', color: '#6B7280', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 },
  sectionCard: { backgroundColor: '#fff', borderRadius: 12, borderWidth: 1, borderColor: '#E5E7EB', overflow: 'hidden' },
  item: { flexDirection: 'row', alignItems: 'center', padding: 16, gap: 12 },
  itemBorder: { borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  itemLabel: { flex: 1, fontSize: 15, color: '#111827' },
  dangerLabel: { color: '#EF4444' },
  version: { textAlign: 'center', color: '#9CA3AF', fontSize: 12, padding: 24 },
});
