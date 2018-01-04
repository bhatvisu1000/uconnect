import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';
import {AlertController } from 'ionic-angular';

import 'rxjs/add/operator/map';
import {Response } from "@angular/http";

import { Storage } from '@ionic/storage';
import {HttpService} from "../../services/HttpService"


import {ResponseReceived} from "../../models/ResponseReceived"
import {MyResponse} from "../../models/MyResponse"
import {Data} from "../../models/response/Data"
import {Header} from "../../models/Header"
import {AuthResponse} from "../../models/response/AuthResponse"

import {Request} from "../../models/Request"

import { AuthService } from "../../services/AuthService";
import {SendRequest} from "../../models/SendRequest"
import {LoginRequestData} from "../../models/login/LoginRequestData"

import {Auth} from "../../models/connection/Auth"

/*
  Generated class for the MySchedule page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
  selector: 'page-my-schedule',
  templateUrl: 'my-schedule.html'
})
export class MySchedulePage {
 listScheduleItems: Data= null;
 public authResponseReceived: ResponseReceived;
 public scheduleResponseReceived: ResponseReceived;
 public authResponse: AuthResponse;
 private sendRequest: SendRequest = null;
 private header: Header = null;
 private auth: Auth = null;
 private loginRequestData: LoginRequestData = null;
 private request: Request = null;

  constructor(public navCtrl: NavController, public navParams: NavParams,  public alertCtrl: AlertController, public authService: AuthService, public storage: Storage, public httpService: HttpService ) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad MySchedulePage');
  }
  
  public searchSchedule(event){
    
       
      let alert = this.alertCtrl.create({
          title: 'New Friend!',
          message: event.target.value+'Your friend, Obi wan Kenobi, just approved your friend request!',
          buttons: ['Ok']
        });
        alert.present()
  }

  ngOnInit() {
    this.loadAllScheduleData();
  }

loadAllScheduleData(){
    this.authResponseReceived = this.authService.responseReceived;

    this.storage.get('Auth').then((val) => {
      console.log('Your age is', val);
      this.auth = val;
    });
    
    
    this.loginRequestData = new LoginRequestData(this.auth);
    
    
    this.header= new Header("Schedule", "GetMyAllSchedules", "None");

    
    this.request= new Request(this.header, this.loginRequestData);

    this.sendRequest= new SendRequest(this.request);


    console.log(this.request);
    console.log("registeration Service json data " +     JSON.stringify(this.sendRequest));
    console.log(JSON.stringify(this.sendRequest));
    this.httpService.submitRequest(this.sendRequest)
      .subscribe(
        (response: Response) => {
          this.scheduleResponseReceived = response.json();
          this.listScheduleItems = this.scheduleResponseReceived.MyResponse.Data;
          console.log(this.scheduleResponseReceived);
         },
        err => console.log('error ' + err.json().message),
        () => console.log('Schedule List Complete')
      );


  }
}
