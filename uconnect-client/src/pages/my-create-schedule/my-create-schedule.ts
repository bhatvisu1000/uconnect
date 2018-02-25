import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';
import {AlertController } from 'ionic-angular';

import {  ViewChild, ElementRef } from '@angular/core';
import {  LoadingController, ToastController } from 'ionic-angular';
import { Geolocation } from '@ionic-native/geolocation';


import 'rxjs/add/operator/map';

import {Invitee} from "../../models/schedule/Invitee"
import {ScheduleDetails} from "../../models/schedule/ScheduleDetails"
import {Schedule} from "../../models/schedule/Schedule"

import {Auth} from "../../models/connection/Auth"

import {HttpService} from "../../services/HttpService"
import {SendRequest} from "../../models/SendRequest"
import {Header} from "../../models/Header"
import {Request} from "../../models/Request"

import { Response } from "@angular/http";

declare var google : any;


class Event {
  title: string;
  InviteeName: string;
  startTime: Date;
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
  selector: 'page-my-create-schedule',
  templateUrl: 'my-create-schedule.html'
})
export class MyCreateSchedulePage {

@ViewChild('map') mapRef : ElementRef;

 targetMemberid: String;
 targetFirstName: String;
 targetLastName: String;
 invitee: Invitee;
 event: Event;
 auth: Auth;
 scheduleDetails: ScheduleDetails;
 schedule: Schedule;
 private sendRequest: SendRequest = null;
 header: Header;
 request: Request;
 chromeReleased = '2008-09-02';
 startTime;
 endTime;
 startDate;
 endDate;

 constructor(public navCtrl: NavController, public navParams: NavParams,  public alertCtrl: AlertController, public httpService: HttpService,
 public geolocation: Geolocation,
  public loadingCtrl: LoadingController, public toastCtrl: ToastController) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad MySchedulePage');
    this.showMap();
  }

showMap()
{
  //const loader = this.loadingCtrl.create({content:'Getting Current Location'});
  //loader.present();
  this.geolocation.getCurrentPosition().then(position =>
  {
    //loader.dismiss();
    const location = new google.maps.LatLng(position.coords.latitude, 
      position.coords.longitude);
      console.log( location);
    
      const options = {
      center: location,
      zoom: 10,
      streetViewControl : true,
      mapTypeId : 'roadmap'    
    };
    // const map = new google.maps.Map(this.mapRef.nativeElement, options);
    const map = new google.maps.Map(document.getElementById('map'), options);
    var marker = this.addMarker(location, map);

    alert("Location: " + this.event.location);

    // var searchBox = new google.maps.places.SearchBox(this.place);
    var searchBox = new google.maps.places.SearchBox(document.getElementById('mapsearch'));
    google.maps.event.addListener(searchBox, 'places_changed', function(){
      var places = searchBox.getPlaces();
      var bounds = new google.maps.LatLngBounds();
      var i,place;
      for(i=0;place = places[i];i++)
      {
        bounds.extend(place.geometry.location);
        marker.setPosition(place.geometry.location);
      }
      map.fitBounds(bounds);
      map.setZoom(15);
    });
  }).catch(error => {
    console.log(error);
   // loader.dismiss();
    const toast = this.toastCtrl.create({message:'Unable to find the current location',
  duration:2000}
  );
  toast.present();
  });
}

addMarker(position, map)
{
  return new google.maps.Marker({
    position, map
  });
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
  	this.startDate= '2018-01-14T12:30';
  	this.endDate= '2018-01-14T';
  	this.event.InviteeName = this.targetFirstName + ' ' + this.targetLastName;
  }	




  public submitCreateSchedule() {
  	let inviteeArray: Array<Invitee> = new Array();
  	this.invitee = new Invitee('Member', Number(this.targetMemberid), 'N');
    inviteeArray.push(this.invitee);
    
    this.scheduleDetails = new ScheduleDetails(this.event.title, 'Member', Number(this.auth.EntityId), this.event.location, '2017-12-29 12:12:12', '2017-12-29 01:12:12', 30);

    this.schedule = new Schedule(this.scheduleDetails, inviteeArray, null, null, null, null, this.auth);

	this.header= new Header("Schedule", "NewSchedule", "None");

    
    this.request= new Request(this.header, this.schedule);

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
