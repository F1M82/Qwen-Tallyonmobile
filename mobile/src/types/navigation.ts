import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BottomTabScreenProps as RNBottomTabScreenProps } from '@react-navigation/bottom-tabs';

export type RootStackParamList = {
  Main: undefined;
  Login: undefined;
  Register: undefined;
  VoiceEntry: undefined;
  InvoiceScan: undefined;
  PaymentDetection: { paymentId?: string };
  // Fix: PartyList accepts an optional callback for party selection
  PartyList: { onSelect?: (party: any) => void } | undefined;
  PartyDetail: { partyId: string };
  VoucherEntry: undefined;
  VoucherList: undefined;
  VoucherDetail: { voucherId: string };
  Compliance: undefined;
  BankReconciliation: undefined;
  GSTReconciliation: undefined;
  AuditTrail: undefined;
  TaxMindChat: undefined;
  Reports: undefined;
  Settings: undefined;
};

export type BottomTabParamList = {
  Dashboard: undefined;
  Vouchers: undefined;
  Reconciliation: undefined;
  Reports: undefined;
  Settings: undefined;
};

export type RootStackScreenProps<T extends keyof RootStackParamList> =
  NativeStackScreenProps<RootStackParamList, T>;

export type BottomTabScreenProps<T extends keyof BottomTabParamList> =
  RNBottomTabScreenProps<BottomTabParamList, T>;

declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
