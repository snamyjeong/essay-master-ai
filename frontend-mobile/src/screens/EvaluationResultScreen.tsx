import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native'; // useRoute import
import SoftCard from '../components/SoftCard';
import CustomButton from '../components/CustomButton';

// 평가 데이터 타입 정의 (선택 사항이지만 타입스크립트 사용 시 유용)
interface EvaluationData {
  score: number;
  feedback: {
    goodPoints: string;
    improvements: string;
  };
}

// RouteParams 타입 정의
type EvaluationResultScreenRouteProp = {
  params: {
    evaluationData: EvaluationData;
  };
};

export default function EvaluationResultScreen() {
  const navigation = useNavigation();
  const route = useRoute<EvaluationResultScreenRouteProp>(); // useRoute 사용

  // route.params에서 evaluationData 추출 (안전하게 처리)
  const { evaluationData } = route.params || {};

  const handleGoBack = () => {
    navigation.goBack();
  };

  // evaluationData가 없을 경우를 대비한 렌더링 처리
  if (!evaluationData) {
    return (
      <View style={styles.container}>
        <SoftCard style={styles.card}>
          <Text style={styles.title}>오류</Text>
          <Text style={styles.resultText}>평가 결과를 불러올 수 없습니다.</Text>
          <CustomButton
            title="🔙 돌아가기"
            onPress={handleGoBack}
            style={styles.backButton}
          />
        </SoftCard>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <SoftCard style={styles.card}>
        {/* 기획 변경(용어 통일성): '논술'에서 '서술형 학습' 중심으로 변경 */}
        <Text style={styles.title}>🎯 서술형 심화학습 평가 결과</Text>
        
        <View style={styles.resultItem}>
          <Text style={styles.resultLabel}>🏆 총점:</Text>
          <Text style={styles.resultValue}>{evaluationData.score}점 / 100점</Text>
        </View>

        <View style={styles.resultItem}>
          <Text style={styles.resultLabel}>👍 잘한 점:</Text>
          <Text style={styles.resultText}>{evaluationData.feedback.goodPoints}</Text>
        </View>

        <View style={styles.resultItem}>
          <Text style={styles.resultLabel}>🛠️ 보완할 점:</Text>
          <Text style={styles.resultText}>{evaluationData.feedback.improvements}</Text>
        </View>

        <CustomButton
          title="🔙 돌아가기"
          onPress={handleGoBack}
          style={styles.backButton}
        />
      </SoftCard>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6',
    padding: 20,
  },
  card: {
    // SoftCard 자체 스타일을 유지하면서 추가 여백 등을 줄 수 있습니다.
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 25,
    textAlign: 'center',
    color: '#333',
  },
  resultItem: {
    marginBottom: 15,
  },
  resultLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#444',
    marginBottom: 5,
  },
  resultValue: {
    fontSize: 18,
    color: '#1E90FF',
    fontWeight: 'bold',
  },
  resultText: {
    fontSize: 16,
    color: '#555',
    lineHeight: 24,
  },
  backButton: {
    marginTop: 20,
  },
});
