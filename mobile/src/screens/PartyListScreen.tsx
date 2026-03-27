import React, { useState } from 'react';
import { View, Text, StyleSheet, FlatList, TextInput, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useNavigation, useRoute } from '@react-navigation/native';
import { partyAPI } from '../services/api';

export default function PartyListScreen() {
  const navigation = useNavigation();
  const route = useRoute();
  const { onSelect } = (route.params as any) || {};
  const [search, setSearch] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['parties'],
    queryFn: () => partyAPI.list(),
  });

  const parties: any[] = data?.data || [];
  const filtered = parties.filter((p) =>
    p.name?.toLowerCase().includes(search.toLowerCase()),
  );

  function handleSelect(party: any) {
    if (onSelect) {
      onSelect(party);
      navigation.goBack();
    } else {
      navigation.navigate('PartyDetail' as never, { partyId: party.id } as never);
    }
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Ionicons name="arrow-back" size={24} color="#111827" />
        </TouchableOpacity>
        <Text style={styles.title}>Parties</Text>
        <View style={{ width: 24 }} />
      </View>

      <View style={styles.searchBox}>
        <Ionicons name="search-outline" size={18} color="#9CA3AF" />
        <TextInput
          style={styles.searchInput}
          placeholder="Search parties..."
          value={search}
          onChangeText={setSearch}
        />
      </View>

      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.item} onPress={() => handleSelect(item)}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>{item.name?.charAt(0) || 'P'}</Text>
            </View>
            <View style={styles.info}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.group}>{item.group || 'Sundry Debtors'}</Text>
            </View>
            <Ionicons name="chevron-forward" size={18} color="#9CA3AF" />
          </TouchableOpacity>
        )}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <Text style={styles.empty}>{isLoading ? 'Loading...' : 'No parties found'}</Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', padding: 20, paddingTop: 60, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#111827' },
  searchBox: { flexDirection: 'row', alignItems: 'center', margin: 16, backgroundColor: '#fff', borderRadius: 10, borderWidth: 1, borderColor: '#E5E7EB', paddingHorizontal: 12, gap: 8 },
  searchInput: { flex: 1, fontSize: 15, paddingVertical: 12, color: '#111827' },
  list: { paddingHorizontal: 16, paddingBottom: 24 },
  item: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 12, padding: 14, gap: 12 },
  avatar: { width: 42, height: 42, borderRadius: 21, backgroundColor: '#2563EB', justifyContent: 'center', alignItems: 'center' },
  avatarText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  info: { flex: 1 },
  name: { fontSize: 15, fontWeight: '600', color: '#111827' },
  group: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  separator: { height: 8 },
  empty: { textAlign: 'center', color: '#6B7280', marginTop: 48, fontSize: 15 },
});
