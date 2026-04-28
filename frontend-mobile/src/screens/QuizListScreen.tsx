import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const QuizListScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>AI가 생성한 퀴즈 리스트가 여기에 표시됩니다.</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff' },
  text: { fontSize: 18, color: '#666' },
});

export default QuizListScreen;
