import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';
import {AlertController } from 'ionic-angular';

import 'rxjs/add/operator/map';

import {Invitee} from "../../models/schedule/Invitee"
import {ScheduleDetails} from "../../models/schedule/ScheduleDetails"
import {CreateScheduleData} from "../../models/schedule/CreateScheduleData"

import {Auth} from "../../models/connection/Auth"

import {HttpService} from "../../services/HttpService"
import {SendRequest} from "../../models/SendRequest"
import {Header} from "../../models/Header"
import {Request} from "../../models/Request"

import { Response } from "@angular/http";

class Event {
  title: string;
  InviteeName: string;
  startTime: string;
  endTime: string;
  location: string;
  allDay: boolean;
}


/*
  Generated class for the MySchedule page.

  See http://ionicframework.com/docs/v2/components/#navigation for more info on
  Ionic pages and navigation.
*/
@Component({
  selector: 'page-my--create-schedule',
  templateUrl: 'my-create-schedule.html'
})
export class MyCreateSchedulePage {
 targetMemberid: String;
 targetFirstName: String;
 targetLastName: String;
 invitee: Invitee;
 event: Event;
 auth: Auth;
 scheduleDetails: ScheduleDetails;
 createScheduleData: CreateScheduleData;
 private sendRequest: SendRequest = null;
 header: Header;
 request: Request;

 constructor(public navCtrl: NavController, public navParams: NavParams,  public alertCtrl: AlertController, public httpService: HttpService) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad MySchedulePage');
  }

  searchSchedule(event) {
      let alert = this.alertCtrl.create({
          title: 'New Friend!',
          message: event.target.value+'Your friend, Obi wan Kenobi, just approved your friend request!',
          buttons: ['Ok']
        });
        alert.present();
  }

  ngOnInit() {
  	this.targetMemberid = this.navParams.get('targetMemberid');
  	this.targetFirstName = this.navParams.get('targetFirstName');
  	this.targetLastName = this.navParams.get('targetLastName');
  	this.auth = this.navParams.get('auth');

  	this.event = new Event();
  	this.event.startTime = '2017';
  	this.event.endTime = '2017';
  	this.event.InviteeName = this.targetFirstName + ' ' + this.targetLastName;
  }




  public submitCreateSchedule() {
  	let inviteeArray: Array<Invitee> = new Array();
  	this.invitee = new Invitee('Member', Number(this.targetMemberid), 'N');
    inviteeArray.push(this.invitee);
    
    this.scheduleDetails = new ScheduleDetails(this.event.title, 'Member', Number(this.auth.EntityId), this.event.location, '2017-12-29 12:12:12', '2017-12-29 01:12:12', 30);

    this.createScheduleData = new CreateScheduleData(this.scheduleDetails, inviteeArray, null, null, null, null, this.auth);

	this.header= new Header("Schedule", "NewSchedule", "None");

    
    this.request= new Request(this.header, this.createScheduleData);

    this.sendRequest= new SendRequest(this.request);
    this.httpService.submitRequest(this.sendRequest)
      .subscribe(
        (response: Response) => {
          let connectionResponseReceived = response.json();
          
          console.log(connectionResponseReceived);
         },
        err => console.log('error ' + err.json().message),
        () => console.log('Authentication Complete')
      );
  }

    
}
