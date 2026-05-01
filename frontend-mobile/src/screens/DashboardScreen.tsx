import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import SoftCard from '../components/SoftCard'; 
import CustomButton from '../components/CustomButton'; 

export default function DashboardScreen() {
  const navigation = useNavigation();
  const userName = "정성남";
  const currentLevel = "Lv.5 메타인지 마스터";
  const progress = 75;
  const announcements = [
    "서술형 심화학습 기능이 업데이트되었습니다!",
    "주간 학습 리포트가 발행되었습니다. 확인해보세요.",
    "시스템 점검 안내: 5/10 03:00 ~ 05:00",
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      {/* [수정] ScrollView 하단 여백 추가 */}
      <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 100 }}>
        <View style={styles.header}>
          <Text style={styles.greeting}>오늘도 열공하세요! 🔥</Text>
          <Text style={styles.userName}>{userName} 마스터님</Text>
        </View>

        <SoftCard style={styles.card}>
          <Text style={styles.cardTitle}>나의 학습 현황</Text>
          <View style={styles.progressContainer}>
            <Text style={styles.progressText}>전체 진도율</Text>
            <Text style={styles.progressPercent}>{progress}%</Text>
          </View>
          <View style={styles.progressBarBackground}>
            <View style={[styles.progressBarFill, { width: `${progress}%` }]} />
          </View>
          <View style={styles.levelContainer}>
            <Text style={styles.levelText}>🏅 {currentLevel}</Text>
          </View>
        </SoftCard>

        <SoftCard style={styles.card}>
          <View style={styles.sectionHeader}>
            <Text style={styles.cardTitle}>📢 공지사항</Text>
            <TouchableOpacity><Text style={styles.moreButtonText}>더보기</Text></TouchableOpacity>
          </View>
          {announcements.map((notice, index) => (
            <View key={index} style={styles.announcementItem}>
              <Text style={styles.announcementBullet}>•</Text>
              <Text style={styles.announcementText} numberOfLines={1}>{notice}</Text>
            </View>
          ))}
        </SoftCard>

        <View style={styles.quickMenuContainer}>
          <CustomButton title="📄 PDF 분석" onPress={() => navigation.navigate('UploadPdf')} style={styles.quickMenuButton} />
          <View style={{ width: 10 }} /> 
          <CustomButton title="📝 퀴즈함 이동" onPress={() => navigation.navigate('QuizListTab')} style={styles.quickMenuButton} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#F3F4F6' },
  container: { flex: 1, paddingHorizontal: 20, paddingTop: 20 },
  header: { marginBottom: 25 },
  greeting: { fontSize: 22, fontWeight: 'bold', color: '#1F2937' },
  userName: { fontSize: 18, color: '#4B5563', marginTop: 5 },
  card: { marginBottom: 20, backgroundColor: '#FFFFFF' },
  cardTitle: { fontSize: 18, fontWeight: 'bold', color: '#1F2937', marginBottom: 15 },
  progressContainer: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  progressText: { fontSize: 16, color: '#4B5563', fontWeight: '500' },
  progressPercent: { fontSize: 18, fontWeight: 'bold', color: '#1E90FF' },
  progressBarBackground: { height: 10, backgroundColor: '#E5E7EB', borderRadius: 5, overflow: 'hidden', marginBottom: 15 },
  progressBarFill: { height: '100%', backgroundColor: '#1E90FF', borderRadius: 5 },
  levelContainer: { paddingTop: 10, borderTopWidth: 1, borderTopColor: '#F3F4F6' },
  levelText: { fontSize: 16, color: '#4B5563', fontWeight: 'bold' },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 15 },
  announcementItem: { flexDirection: 'row', marginBottom: 10, alignItems: 'center' },
  announcementBullet: { fontSize: 16, color: '#1E90FF', marginRight: 8 },
  announcementText: { fontSize: 15, color: '#374151', flexShrink: 1 },
  moreButtonText: { color: '#1E90FF', fontSize: 14, fontWeight: 'bold' },
  quickMenuContainer: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 5 },
  quickMenuButton: { flex: 1 },
});