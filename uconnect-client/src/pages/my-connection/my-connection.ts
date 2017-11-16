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
	listConnectionItems: Connections[]= null;
  listNewConnectionItems: Connections[]= null;
  listAllConnectionItems: Connections[]= null;
  listFavouriteConnectionItems: Connections[]= null;
  listGroupConnectionItems: Connections[]= null;
  public queryText: string="";
  public authResponseReceived: ResponseReceived;
  public connectionResponseReceived: ResponseReceived;
  public authResponse: AuthResponse;
  private sendRequest: SendRequest = null;
  segment: string ="All"

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

          /**for (var i=0; i< this.listConnectionItems.length; i++) {
            this.listAllConnectionItems.push(this.listConnectionItems[i]);
            if(this.listConnectionItems[i].Status='Awaiting Response'){
              this.listNewConnectionItems.push(this.listConnectionItems[i]);
            }

            if(this.listConnectionItems[i].Favorite='1'){
              this.listFavouriteConnectionItems.push(this.listConnectionItems[i]);
            }
          }
**/
          console.log(this.listConnectionItems);
         },
        err => console.log('error ' + err.json().message),
        () => console.log('Authentication Complete')
      );
  }
  ionViewWillEnter() {
      
    console.log('this.responseReceived ' + this.authResponseReceived);
    this.loadConnectionData();
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

  favourite(favouriteOrUnFavoutite: string){
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

  /**schedule(memberId: string) {
    let alert = this.alertCtrl.create({
      title: 'New Friend!',
      message: 'Your friend, Obi wan Kenobi, just approved your friend request!',
      buttons: ['Ok']
    });
    alert.present()
  }**/

  deleteConnection(memberId: string) {
    this.sendRequest = this.connectionService.createDeleteRequest(this.authResponseReceived.MyResponse.Data[0].AuthResponse.EntityId);
  }

 updateConnection(memberId: string, action: string) {
    this.sendRequest = this.connectionService.createUpdateConnectionsRequest(memberId, action);
    this.httpService.submitRequest(this.sendRequest)
      .subscribe(
        (response: Response) => {
          this.connectionResponseReceived = response.json();
          this.loadConnectionData();
          console.log(this.listConnectionItems);
         },
        err => console.log('error ' + err.json().message),
        () => console.log('Authentication Complete')
      );
  }

searchConnection(event: string){
  let alert = this.alertCtrl.create({
      title: 'New Friend!',
      message: this.queryText+event+'Your friend, Obi wan Kenobi, just approved your friend request!',
      buttons: ['Ok']
    });
    alert.present()
}



  schedule(memberId: string) {
  var customTemplate =
      '<ion-toggle>enable</ion-toggle>' +
      '<label class="item item-input"><input type="text" placeholder="your address"></label><button ion-button>Default</button>';
    let confirm = this.alertCtrl.create({
     
      title: 'Use this lightsaber?',
      message: customTemplate,
      buttons: [
        {
          text: 'Disagree',
          handler: () => {
            console.log('Disagree clicked');
          }
        },
        {
          text: 'Agree',
          handler: () => {
            console.log('Agree clicked');
          }
        }
      ]
    });
    confirm.present();
    
    }

}
