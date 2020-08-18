import React, { useState, useEffect } from "react";
import Colors from '../constants/colors';
import { StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, TextInput, Text, View, Modal, Linking, Platform, Image, Alert, FlatList } from 'react-native';
import * as Font from "expo-font";
import { Entypo, MaterialIcons } from '@expo/vector-icons';
import * as Localization from 'expo-localization';
import i18n from 'i18n-js';
import { widthPercentageToDP as wp, heightPercentageToDP as hp } from 'react-native-responsive-screen';
import EntryCard from '../components/entryRecordCard';
import axios from "axios";
import AsyncStorage from "@react-native-community/async-storage";
import Constants from '../constants/text'

const fetchFonts = () => {
    console.log("loading font");
    return Font.loadAsync({
        "Quicksand-regular": require("../assets/fonts/Quicksand-Regular.ttf"),
        "Quicksand-medium": require("../assets/fonts/Quicksand-Medium.ttf"),
        "Quicksand-Bold": require("../assets/fonts/Quicksand-Bold.ttf"),
        "Quicksand-SemiBold": require("../assets/fonts/Quicksand-SemiBold.ttf"),
    });
};

export default function EntryRecords({ navigation }) {

    const [userData, setUserData] = useState({});
    const [dataLoaded, setDataLoaded] = useState(false);
    const [historyData, setHistoryData] = useState({});

    const request_history = async () => {
        try {

            let response = await AsyncStorage.getItem("userData")
            response = JSON.parse(response);

            axios
                .get(`${Constants.ApiLink}/api/history/${response.data.user_email}`)
                .then(async function (response) {
                    // handle success

                    try {
                        const jsonValue = response.data.data
                        console.log(jsonValue)
                        setHistoryData(jsonValue)
                        setDataLoaded(true);
                        console.log("data: " + jsonValue);
                    } catch (e) {
                        // saving error
                        console.log("Got error while storing data to async" + e);
                    }
                })
                .catch(function (error) {
                    // handle error
                    console.log("ERROR ON HOME", error);
                })
                .finally(function () {
                    // always executed
                });
            // await fetchFonts();
        } catch (e) {
            console.warn(e);
        } finally {
            setDataLoaded(true);
            // Hiding the SplashScreen

        }
    }

    var radio_props = [
        { label: 'High ', value: 0 },
        { label: 'Medium ', value: 1 },
        { label: 'Low ', value: 2 }
    ];



    const init = async () => {
        try {
            // Keep on showing the SlashScreen


            await fetchFonts();
        } catch (e) {
            console.warn(e);
        } finally {
            setDataLoaded(true);
            // Hiding the SplashScreen

        }
    }

    useEffect(() => {
        init();
        request_history();
    }, []);


    if (!dataLoaded) {
        return (
            <View>
                <Text>Loading....</Text>
            </View>
        );
    } else {
        return (
            <View style={{ paddingHorizontal: wp("4%"), backgroundColor: "white" }}>
                <View style={{ paddingBottom: "7%", paddingTop: "4%" }}>
                    <TouchableOpacity style={{ position: "absolute", top: hp("2%") }}>
                        <MaterialIcons name="keyboard-backspace" size={24} color="black" />
                    </TouchableOpacity>
                    <View style={{ alignItems: "center", flexGrow: 1 }}>
                        <Text style={{ fontFamily: "Quicksand-Bold", fontSize: 20, color: "black", textAlign: "center" }} >Your reports</Text>
                    </View>
                    
                </View>
                <FlatList
                    style={{ marginBottom: hp("10%") }}
                    numColumns={1}                  // set number of columns 

                    data={historyData}
                    renderItem={({ item }) => <EntryCard props={item} />}
                    keyExtractor={item => item.id}
                />
            </View>
        );
    }
}

const styles = StyleSheet.create({
    row: {
        flex: 1,
        justifyContent: "space-around",
    }
});