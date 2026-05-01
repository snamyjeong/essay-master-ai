import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import HomeScreen from '../screens/HomeScreen';
import QuizScreen from '../screens/QuizScreen';
import EvaluationResultScreen from '../screens/EvaluationResultScreen';
import TypingScreen from '../screens/TypingScreen';
import { Ionicons } from '@expo/vector-icons';

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

// 학습확인 탭 내부에 Stack Navigator 구성
function QuizStackScreen() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Quiz" component={QuizScreen} />
      <Stack.Screen name="EvaluationResult" component={EvaluationResultScreen} />
    </Stack.Navigator>
  );
}

export default function AppNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: '#1E90FF',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: { backgroundColor: '#F3F4F6' },
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'HomeScreen') {
            iconName = focused ? 'create' : 'create-outline';
          } else if (route.name === 'QuizStack') {
            iconName = focused ? 'checkmark-circle' : 'checkmark-circle-outline';
          } else if (route.name === 'TypingScreen') {
            iconName = focused ? 'text' : 'text-outline';
          } else {
            iconName = 'help-circle'; // Fallback icon
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen
        name="HomeScreen"
        component={HomeScreen}
        options={{
          title: '📝 내용입력',
        }}
      />
      <Tab.Screen
        name="QuizStack"
        component={QuizStackScreen}
        options={{
          title: '💡 학습확인',
        }}
      />
      <Tab.Screen
        name="TypingScreen"
        component={TypingScreen}
        options={{
          title: '✍️ 타자연습',
        }}
      />
    </Tab.Navigator>
  );
}
