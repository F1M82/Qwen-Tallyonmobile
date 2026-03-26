import { NativeStackScreenProps } from '@react-navigation/native-stack';

export type RootStackParamList = {
  Main: undefined;
  Login: undefined;
  Register: undefined;
  VoiceEntry: undefined;
  InvoiceScan: undefined;
  PaymentDetection: { paymentId?: string };
  PartyList: undefined;
  PartyDetail: { partyId: string };
  VoucherDetail: { voucherId: string };
  Compliance: undefined;
  BankReconciliation: undefined;
  GSTReconciliation: undefined;
  AuditTrail: undefined;
  TaxMindChat: undefined;
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
  NativeStackScreenProps<BottomTabParamList, T>;

declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
