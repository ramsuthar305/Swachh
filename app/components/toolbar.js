import React, { useState, useEffect } from 'react';
import { Camera } from 'expo-camera';
import { Ionicons } from '@expo/vector-icons';
import { Col, Row, Grid } from "react-native-easy-grid";
import { View, TouchableWithoutFeedback, TouchableOpacity } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { MaterialIcons } from '@expo/vector-icons';
import styles from '../constants/styles';
import * as Location from 'expo-location';
import axios from "axios";
import Constants from '../constants/text';
import AsyncStorage from "@react-native-community/async-storage";
export default function Toolbar({ cameraRef, navigation }) {
    const [location, setLocation] = useState(null);
    const [errorMsg, setErrorMsg] = useState(null);
    const [userData, setuserData] = useState({});

    useEffect(() => {
        (async () => {
            let { status } = await Location.requestPermissionsAsync();
            if (status !== 'granted') {
                setErrorMsg('Permission to access location was denied');
            }

            let location = await Location.getCurrentPositionAsync({});
            setLocation(location);
        })();
    });



    const [capturing, setCapturing] = useState(false)
    const [image, setImage] = useState(null)
    const [IsImage, setIsImage] = useState(false)

    async function takePicture() {

        if (cameraRef) {
            setCapturing(true)
            const options = { quality: 0.1, base64: true, uri: true };
            let photo = await cameraRef.takePictureAsync(options);
            setCapturing(false)
            setIsImage(true)
            setImage(photo.base64)
            await cameraRef.pausePreview()
        }

    }

    async function uploadData() {
        setIsImage(false)
        let response=await AsyncStorage.getItem("userData")
        
        response = JSON.parse(response);
        console.log('\n\n\n\noriginal data:'+JSON.stringify(response.data.user_email))
        let location = await Location.getCurrentPositionAsync({});
       
        const data = {
            "image_link": image,
            "grievance_id": Math.random().toString(36).substring(7),
            "user_id": response.data.user_email,
            "grievance_type": "unpredicted",
            "latitude": location.coords.latitude,
            "longitude": location.coords.longitude,
        }

        console.log('this is your data: ' + JSON.stringify(data))
        axios
            .post(`${Constants.ApiLink}/uploader`, data)
            .then(async function (response) {
                // handle success

                try {
                    const jsonValue = JSON.stringify(response.data);
                    await AsyncStorage.setItem("value", jsonValue);
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
        // console.log('This is my base 64 image', image)
        await cameraRef.resumePreview()
    }

    async function account() {
        navigation.navigate('Profile')
    }

    return (
        <Grid style={styles.bottomToolbar}>
            <Row>
                <Col style={styles.alignCenter}>
                    <TouchableOpacity onPress={() => navigation.navigate('EntryRecords')}>
                        <MaterialIcons name="history" size={30} color="white" />
                    </TouchableOpacity>
                </Col>

                <Col size={2} style={styles.alignCenter}>
                    <TouchableWithoutFeedback
                        onPress={takePicture}>
                        <View style={[styles.captureBtn, capturing && styles.captureBtnActive]}>
                            {capturing && <View style={styles.captureBtnInternal} />}
                        </View>
                    </TouchableWithoutFeedback>


                </Col>
                {
                    IsImage ?
                        <Col style={styles.alignCenter}>
                            <TouchableOpacity onPress={uploadData}>
                                <Feather name="check" size={30} color="white" />
                            </TouchableOpacity>
                        </Col> : <Col style={styles.alignCenter}>
                            <TouchableOpacity onPress={account}>
                                <MaterialCommunityIcons name="account" size={30} color="white" />
                            </TouchableOpacity>
                        </Col>
                }
            </Row>
        </Grid>);
}