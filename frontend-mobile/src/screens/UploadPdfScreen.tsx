import React, { useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator, Alert } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import SoftCard from '../components/SoftCard';
import CustomButton from '../components/CustomButton';

const UploadPdfScreen: React.FC = () => {
  const [selectedFileName, setSelectedFileName] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChoosePdf = async () => {
    const result = await DocumentPicker.getDocumentAsync({ type: 'application/pdf' });
    if (!result.canceled) setSelectedFileName(result.assets[0].name);
  };

  return (
    // [수정] 중앙 정렬된 View 하단에 메뉴 가림 방지 여백 추가
    <View style={[styles.container, { paddingBottom: 100 }]}>
      <Text style={styles.title}>📑 PDF 학습 자료 분석</Text>
      <SoftCard style={styles.card}>
        <CustomButton title="📂 PDF 파일 선택" onPress={handleChoosePdf} disabled={isLoading} />
        {selectedFileName && (
          <View style={styles.infoBox}>
            <Text style={styles.fileName}>선택된 파일: {selectedFileName}</Text>
            <CustomButton title={isLoading ? "분석 중..." : "🚀 AI 분석 시작"} onPress={() => setIsLoading(true)} style={styles.uploadButton} />
          </View>
        )}
        {isLoading && <ActivityIndicator size="large" color="#1E90FF" style={{ marginTop: 20 }} />}
      </SoftCard>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20, backgroundColor: '#F3F4F6' },
  title: { fontSize: 26, fontWeight: 'bold', marginBottom: 30, textAlign: 'center' },
  card: { padding: 20, alignItems: 'center' },
  infoBox: { marginTop: 25, alignItems: 'center', width: '100%' },
  fileName: { marginBottom: 15, fontSize: 16, color: '#555' },
  uploadButton: { backgroundColor: '#28a745', width: '100%' },
});

export default UploadPdfScreen;