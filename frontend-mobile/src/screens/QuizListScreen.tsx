import React from 'react'; // React 라이브러리 임포트
import { View, Text, StyleSheet, ScrollView } from 'react-native'; // 기본 UI 컴포넌트 임포트
import SoftCard from '../components/SoftCard'; // UI 통일성을 위한 카드 컴포넌트 임포트
import CustomButton from '../components/CustomButton'; // UI 통일성을 위한 버튼 컴포넌트 임포트

const QuizListScreen = () => {
  return (
    // 스크롤이 가능하도록 ScrollView를 사용하고, 하단 여백을 주어 잘리지 않도록 설정합니다.
    <ScrollView style={styles.container} contentContainerStyle={styles.scrollContent}>
      {/* 화면 제목 (기획 변경 반영) */}
      <Text style={styles.title}>🦉 학습 퀴즈 리스트</Text>
      
      {/* 1. Empty State: 추후 백엔드에서 받아온 데이터가 비어있을 때 보여줄 UI입니다. */}
      <SoftCard style={styles.card}>
        <Text style={styles.emptyTitle}>아직 생성된 퀴즈가 없습니다.</Text>
        <Text style={styles.emptySub}>문서를 업로드하고 AI 분석을 통해 퀴즈를 만들어보세요.</Text>
      </SoftCard>

      {/* 2. Mockup Item: 추후 백엔드에서 데이터를 받아왔을 때 반복문(map)으로 렌더링할 아이템의 예시입니다. */}
      <SoftCard style={styles.card}>
        {/* 퀴즈 제목 */}
        <Text style={styles.quizTitle}>📌 [예시] AI 기술 발전과 사회적 영향</Text>
        {/* 퀴즈 메타 정보 (문항 수 등) */}
        <Text style={styles.quizInfo}>총 3문제 • 서술형 및 키워드 포함</Text>
        {/* 퀴즈 시작 버튼 */}
        <CustomButton 
          title="🚀 퀴즈 풀기" 
          onPress={() => console.log('퀴즈 화면으로 이동')} // 연동 시 navigation.navigate 적용 예정
          style={styles.startButton} 
        />
      </SoftCard>
      
      {/* 두 번째 예시 아이템 (리스트 느낌을 주기 위해 추가) */}
      <SoftCard style={styles.card}>
        <Text style={styles.quizTitle}>📌 [예시] 클라우드 컴퓨팅의 이해</Text>
        <Text style={styles.quizInfo}>총 5문제 • 단답형 및 서술형 포함</Text>
        <CustomButton 
          title="🚀 퀴즈 풀기" 
          onPress={() => console.log('퀴즈 화면으로 이동')} 
          style={styles.startButton} 
        />
      </SoftCard>
    </ScrollView>
  );
};

// 화면 스타일 정의
const styles = StyleSheet.create({
  // 앱 전체 공통 배경색(#F3F4F6)으로 통일
  container: { flex: 1, backgroundColor: '#F3F4F6' },
  scrollContent: { padding: 20, paddingBottom: 40 }, // 스크롤 내부 여백 설정
  title: { fontSize: 26, fontWeight: 'bold', marginBottom: 20, textAlign: 'center', color: '#333' },
  card: { marginBottom: 15, padding: 20 }, // 개별 리스트 아이템(카드) 간격 및 내부 여백
  
  // Empty State 관련 스타일
  emptyTitle: { fontSize: 18, fontWeight: 'bold', color: '#555', textAlign: 'center', marginBottom: 10 },
  emptySub: { fontSize: 14, color: '#777', textAlign: 'center', lineHeight: 22 },
  
  // 리스트 아이템 관련 스타일
  quizTitle: { fontSize: 18, fontWeight: 'bold', color: '#333', marginBottom: 8 },
  quizInfo: { fontSize: 14, color: '#666', marginBottom: 15 },
  startButton: { marginTop: 5 }, // 버튼 위쪽 여백
});

export default QuizListScreen;