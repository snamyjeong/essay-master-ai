import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Ionicons } from '@expo/vector-icons';

// --- 스크린 임포트 ---
import LoginScreen from '../screens/LoginScreen';
import DashboardScreen from '../screens/DashboardScreen'; // 신규: 메인 대시보드
import HomeScreen from '../screens/HomeScreen';           // 기존: 내용 텍스트 입력
import UploadPdfScreen from '../screens/UploadPdfScreen'; // 신규: PDF 업로드
import QuizListScreen from '../screens/QuizListScreen';   // 신규: 퀴즈 리스트
import QuizScreen from '../screens/QuizScreen';           // 기존: 실제 퀴즈 풀기
import EvaluationResultScreen from '../screens/EvaluationResultScreen'; // 기존: 평가 결과
import TypingScreen from '../screens/TypingScreen';       // 기존: 타자 연습

// 네비게이터 객체 생성
const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// ---------------------------------------------------------
// 1. 메인 하단 탭 네비게이터 (로그인 성공 후 보여질 화면들)
// ---------------------------------------------------------
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false, // 탭 내부 화면들의 상단 기본 헤더 숨김
        tabBarActiveTintColor: '#1E90FF', // 선택된 탭의 아이콘/텍스트 색상 (블루)
        tabBarInactiveTintColor: 'gray',  // 비활성화된 탭 색상
        tabBarStyle: { backgroundColor: '#F3F4F6', paddingBottom: 5 }, // 탭 바 배경색을 앱 공통색으로 통일
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap = 'help-circle';

          // 라우터 이름에 따라 하단 탭 아이콘 동적 할당
          if (route.name === 'DashboardTab') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'InputTab') {
            iconName = focused ? 'create' : 'create-outline';
          } else if (route.name === 'QuizListTab') {
            iconName = focused ? 'library' : 'library-outline';
          } else if (route.name === 'TypingTab') {
            iconName = focused ? 'text' : 'text-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
    {/* 탭 1: 대시보드 (홈) - 중복되는 이모지 제거로 세련된 UI 확보 */}
    <Tab.Screen name="DashboardTab" component={DashboardScreen} options={{ title: '홈' }} />
    {/* 탭 2: 텍스트 직접 입력 - 중복되는 이모지 제거 */}
    <Tab.Screen name="InputTab" component={HomeScreen} options={{ title: '학습입력' }} />
    {/* 탭 3: 내 퀴즈 목록 - 중복되는 이모지 제거 */}
    <Tab.Screen name="QuizListTab" component={QuizListScreen} options={{ title: '학습퀴즈' }} />
    {/* 탭 4: 타자 연습 - 중복되는 이모지 제거 */}
    <Tab.Screen name="TypingTab" component={TypingScreen} options={{ title: '타자연습' }} />
    </Tab.Navigator>
  );
}

// ---------------------------------------------------------
// 2. 최상위 루트 스택 네비게이터 (앱 전체 화면 전환 담당)
// ---------------------------------------------------------
export default function AppNavigator() {
  return (
    // 앱이 켜지면 무조건 'Login' 화면부터 시작합니다.
    <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
      
      {/* --- 인증 영역 --- */}
      <Stack.Screen name="Login">
        {(props) => (
          <LoginScreen 
            {...props} 
            // 로그인 성공 시 'MainTabs'로 화면을 갈아끼웁니다 (뒤로가기 방지).
            onLoginSuccess={() => props.navigation.replace('MainTabs')} 
          />
        )}
      </Stack.Screen>

      {/* --- 메인 앱 영역 (하단 탭 포함) --- */}
      <Stack.Screen name="MainTabs" component={MainTabNavigator} />

      {/* --- 서브 스크린 영역 (하단 탭 없이 집중해야 하는 화면들) --- */}
      {/* 대시보드에서 'PDF 분석' 버튼 클릭 시 넘어오는 화면 */}
      <Stack.Screen name="UploadPdf" component={UploadPdfScreen} />
      
      {/* 퀴즈 목록에서 특정 퀴즈 클릭 시 넘어오는 실제 풀이 화면 */}
      <Stack.Screen name="Quiz" component={QuizScreen} />
      
      {/* 퀴즈 제출 후 넘어오는 결과 화면 */}
      <Stack.Screen name="EvaluationResult" component={EvaluationResultScreen} />

    </Stack.Navigator>
  );
}