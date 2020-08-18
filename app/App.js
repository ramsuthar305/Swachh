import React from 'react';
import * as Font from 'expo-font';
import Login from './screens/Login';
import { createAppContainer } from 'react-navigation';
import { createStackNavigator, HeaderBackButton } from 'react-navigation-stack';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { StyleSheet } from 'react-native';
import GeneralStatusBarColor from './components/GeneralStatusBar';
import Colors from './constants/colors'
import Home from './screens/Home';
import Register from './screens/register';
import EntryRecords from './screens/entryRecord'
import Profile from './screens/Profile'

const AppNavigator = createStackNavigator({
  Login: {
    screen: Login,
    navigationOptions: {
      title: 'Login',
      headerShown: false //this will hide the header
    },
  },
  Home: {
    screen: Home,
    navigationOptions: {
      title: 'Home',
      headerShown: false //this will hide the header
    },
  },
  
  EntryRecords: {
    screen: EntryRecords,
    navigationOptions: {
      title: 'EntryRecords',
      headerShown: false //this will hide the header
    },
  },
  Register:{
    screen: Register,
    navigationOptions:{
      title: 'Register',
      headerShown: false
    }
  },
  Profile:{
    screen: Profile,
    navigationOptions:{
      title: 'Profile',
      headerShown: false
    }
  }
  
},

  {
    initialRouteName: 'Login',
  });

const AppContainer = createAppContainer(AppNavigator);

export default function App() {
  
  Font.loadAsync({
    "Quicksand-regular": require("./assets/fonts/Quicksand-Regular.ttf"),
    "Quicksand-medium": require("./assets/fonts/Quicksand-Medium.ttf"),
    "Quicksand-Bold": require("./assets/fonts/Quicksand-Bold.ttf"),
    "Quicksand-SemiBold": require("./assets/fonts/Quicksand-SemiBold.ttf"),
  });
  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <GeneralStatusBarColor backgroundColor={Colors.primaryColor} barStyle="light-content" />
        <AppContainer />
      </SafeAreaView>
    </SafeAreaProvider>
  )
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
});





