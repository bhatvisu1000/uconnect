import { Component } from '@angular/core';
import { NavController, NavParams } from 'ionic-angular';

import { Storage } from '@ionic/storage';
import {HttpService} from "../../services/HttpService"

import {ConnectionService } from "../../services/ConnectionService";
import {Connections} from "../../models/connection/Connections"
import {AlertController } from 'ionic-angular';
import {ResponseReceived} from "../../models/ResponseReceived"
import {MyResponse} from "../../models/MyResponse"

import {AuthResponse} from "../../models/response/AuthResponse"

import { AuthService } from "../../services/AuthService";
import {SendRequest} from "../../models/SendRequest"

import { Response } from "@angular/http";

@Component({
  selector: 'page-my-connection',
  templateUrl: 'my-connection.html',
  providers: [ConnectionService]
})
export class MyConnectionPage {
	listConnectionItems: Connections[];
  public authResponseReceived: ResponseReceived;
  public connectionResponseReceived: ResponseReceived;
  public authResponse: AuthResponse;
  private sendRequest: SendRequest = null;

  constructor(public navCtrl: NavController, public navParams: NavParams, private connectionService: ConnectionService, public alertCtrl: AlertController, public authService: AuthService, public storage: Storage, public httpService: HttpService) {}

  ionViewDidLoad() {
    console.log('ionViewDidLoad MyConnectionPage load start');
    
    /*this.authResponse = this.storage.get('AuthResponse');*/
    
    this.loadConnectionData();
	  console.log('ionViewDidLoad MyConnectionPage load end');
    
  }

  loadConnectionData(){
    this.authResponseReceived = this.authService.responseReceived;
    this.sendRequest = this.connectionService.createRequest(
        this.authResponseReceived.MyResponse.Data[0].AuthResponse.AuthKey, this.authService.username, this.authResponseReceived.MyResponse.Data[0].AuthResponse.EntityId);
    this.httpService.submitRequest(this.sendRequest)
      .subscribe(
        (response: Response) => {
          this.connectionResponseReceived = response.json();
          this.listConnectionItems = this.connectionResponseReceived.MyResponse.Data[0].Connections;
          console.log(this.listConnectionItems);
         },
        err => console.log('error ' + err.json().message),
        () => console.log('Authentication Complete')
      );
  }
  ionViewWillEnter() {
      
    console.log('this.responseReceived ' + this.authResponseReceived);
  }

  
  
  getItems() {
    let alert = this.alertCtrl.create({
      title: 'New Friend!',
      message: 'Your friend, Obi wan Kenobi, just approved your friend request!',
      buttons: ['Ok']
    });
    alert.present()
  }

  removeItem(){
    let alert = this.alertCtrl.create({
      title: 'New Friend!',
      message: 'Your friend, Obi wan Kenobi, just approved your friend request!',
      buttons: ['Ok']
    });
    alert.present()
  }

  updateResults() {
  let alert = this.alertCtrl.create({
      title: 'New Friend!',
      message: 'Your friend, Obi wan Kenobi, just approved your friend request!',
      buttons: ['Ok']
    });
    alert.present()
    
  }

}
