import React from 'react'; // React 라이브러리를 임포트합니다.
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'; // 하단 탭 네비게이터 생성을 위한 라이브러리입니다.
import { createNativeStackNavigator } from '@react-navigation/native-stack'; // 스택 네비게이터 생성을 위한 라이브러리입니다.
import { Ionicons } from '@expo/vector-icons'; // 아이콘 사용을 위한 라이브러리입니다.

// --- 각 화면 컴포넌트 임포트 (경로 확인 필수) ---
import LoginScreen from '../screens/LoginScreen'; // 로그인 화면
import DashboardScreen from '../screens/DashboardScreen'; // 홈 대시보드 화면
import HomeScreen from '../screens/HomeScreen'; // 학습입력 화면
import QuizListScreen from '../screens/QuizListScreen'; // 학습퀴즈 목록 화면
import TypingScreen from '../screens/TypingScreen'; // 타자연습 화면
import ChatScreen from '../screens/ChatScreen'; // AI 상담 채팅 화면
import UploadPdfScreen from '../screens/UploadPdfScreen'; // PDF 업로드 화면
import QuizScreen from '../screens/QuizScreen'; // 퀴즈 풀이 화면
import EvaluationResultScreen from '../screens/EvaluationResultScreen'; // 평가 결과 화면

const Tab = createBottomTabNavigator(); // 탭 네비게이터 객체 생성
const Stack = createNativeStackNavigator(); // 스택 네비게이터 객체 생성

// ---------------------------------------------------------
// 1. 메인 하단 플로팅 탭 네비게이터 (고정형 타원 팝업 스타일)
// ---------------------------------------------------------
function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false, // 상단 헤더 숨김
        tabBarActiveTintColor: '#1E90FF', // 활성화된 메뉴 색상 (파란색)
        tabBarInactiveTintColor: 'gray', // 비활성화된 메뉴 색상 (회색)
        tabBarHideOnKeyboard: true, // 🚨 [핵심 해결책] 키보드 활성화 시 메뉴바를 숨김!
        tabBarStyle: { // 플로팅 바 스타일 정의
          position: 'absolute', // 화면에 절대 좌표로 배치하여 스크롤에 영향받지 않게 함
          bottom: 40, // 하단에서 40px 위로 올려 시스템 바와의 간섭 완전 제거
          left: 15, // 왼쪽 여백
          right: 15, // 오른쪽 여백
          height: 65, // 메뉴 바의 세로 높이
          borderRadius: 35, // 완전한 타원형 디자인을 위한 라운드 값
          backgroundColor: '#FFFFFF', // 배경색 (흰색)
          elevation: 15, // 안드로이드에서 그림자를 강하게 주어 최상단 레이어로 고정
          shadowColor: '#000', // iOS용 그림자 색상
          shadowOffset: { width: 0, height: 6 }, // iOS용 그림자 오프셋
          shadowOpacity: 0.2, // iOS용 그림자 투명도
          shadowRadius: 8, // iOS용 그림자 퍼짐 정도
          zIndex: 1000, // 컴포넌트 계층상 가장 위에 오도록 설정
          paddingBottom: 5, // 하단 텍스트 여백
        },
        tabBarLabelStyle: { fontSize: 10, fontWeight: 'bold' }, // 메뉴 글자 스타일
        tabBarIcon: ({ focused, color, size }) => { // 탭별 아이콘 설정
          let iconName: any;
          if (route.name === 'DashboardTab') iconName = focused ? 'home' : 'home-outline';
          else if (route.name === 'InputTab') iconName = focused ? 'create' : 'create-outline';
          else if (route.name === 'QuizListTab') iconName = focused ? 'library' : 'library-outline';
          else if (route.name === 'TypingTab') iconName = focused ? 'text' : 'text-outline';
          else if (route.name === 'ChatTab') iconName = focused ? 'chatbox-ellipses' : 'chatbox-ellipses-outline';
          return <Ionicons name={iconName} size={size - 2} color={color} />;
        },
      })}
    >
      {/* 파트너님이 지시하신 순서대로 배치: 홈 -> 학습입력 -> 학습퀴즈 -> 타자연습 -> AI 상담 */}
      <Tab.Screen name="DashboardTab" component={DashboardScreen} options={{ title: '홈' }} />
      <Tab.Screen name="InputTab" component={HomeScreen} options={{ title: '학습입력' }} />
      <Tab.Screen name="QuizListTab" component={QuizListScreen} options={{ title: '학습퀴즈' }} />
      <Tab.Screen name="TypingTab" component={TypingScreen} options={{ title: '타자연습' }} />
      <Tab.Screen name="ChatTab" component={ChatScreen} options={{ title: 'AI 상담' }} />
    </Tab.Navigator>
  );
}

// ---------------------------------------------------------
// 2. 최상위 루트 스택 네비게이터
// ---------------------------------------------------------
export default function AppNavigator() {
  return (
    <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login">
        {(props) => (
          <LoginScreen 
            {...props} 
            onLoginSuccess={() => props.navigation.replace('MainTabs')} 
          />
        )}
      </Stack.Screen>
      <Stack.Screen name="MainTabs" component={MainTabNavigator} />
      <Stack.Screen name="UploadPdf" component={UploadPdfScreen} />
      <Stack.Screen name="Quiz" component={QuizScreen} />
      <Stack.Screen name="EvaluationResult" component={EvaluationResultScreen} />
    </Stack.Navigator>
  );
}