import axios from 'axios';

// IMPORTANT: For Expo Go testing, use your computer's actual IP address instead of localhost.
// Example: http://192.168.x.x:8000/api/v1
const API_BASE_URL = 'http://136.111.211.8:8000/api/v1'; // 모바일 테스트를 위한 실제 IP 주소로 대체

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // [중요] 임시 인증 토큰: 401 Unauthorized 에러 해결을 위해 임시로 추가된 토큰입니다.
    // 실제 프로덕션 환경에서는 사용자 로그인 후 동적으로 발급된 유효한 토큰을 사용해야 합니다.
    // 예: 'Authorization': `Bearer ${userToken}` 와 같이 구현될 예정입니다.
    'Authorization': 'Bearer test-token', 
  },
});

export const generateLearningContent = async (text: string) => {
  try {
    console.log('API Call: generateLearningContent with text:', text);
    const response = await apiClient.post('/learning/generate-content', { text });
    return response.data;
  } catch (error) {
    console.error('Error generating learning content:', error);
    throw error;
  }
};

export const evaluateEssayAnswer = async (essay: string) => {
  try {
    console.log('API Call: evaluateEssayAnswer with essay:', essay);
    const response = await apiClient.post('/learning/evaluate-essay', { essay });
    return response.data;
  } catch (error) {
    console.error('Error evaluating essay answer:', error);
    throw error;
  }
};
