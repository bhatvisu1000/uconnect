import { Injectable } from '@angular/core';

import { Events } from 'ionic-angular';
import { Storage } from '@ionic/storage';

import { Response } from "@angular/http";

import 'rxjs/Rx';

import {SendRequest} from "../models/SendRequest"
import {Request} from "../models/Request"
import {Header} from "../models/Header"
import {MyResponse} from "../models/MyResponse"
import {ResponseReceived} from "../models/ResponseReceived"
import {Auth} from "../models/connection/Auth"
import {LoginRequestData} from "../models/login/LoginRequestData"

import {HttpService} from "./HttpService"

@Injectable()
export class AuthService {
   _favorites: string[] = [];
  HAS_LOGGED_IN = 'hasLoggedIn';
  HAS_SEEN_TUTORIAL = 'hasSeenTutorial';
  private registrationUrl = 'http://localhost:5000/requestPost';
  private request: Request = null;
  private loginRequestData: LoginRequestData = null;
  private auth: Auth = null;
  public responseReceived: ResponseReceived = null
  private header:  Header = null;
  public sendRequest: SendRequest = null;
  

  constructor(
    public events: Events,
    public storage: Storage, private httpService: HttpService
  ) {}

  hasFavorite(sessionName: string): boolean {
    return (this._favorites.indexOf(sessionName) > -1);
  };

  addFavorite(sessionName: string): void {
    this._favorites.push(sessionName);
  };

  removeFavorite(sessionName: string): void {
    let index = this._favorites.indexOf(sessionName);
    if (index > -1) {
      this._favorites.splice(index, 1);
    }
  };

  login(username: string, password: string): SendRequest {
    

    this.validateLogin(username, password);

    this.storage.set(this.HAS_LOGGED_IN, true);
    this.setUsername(username);




    this.events.publish('user:login');

    return this.sendRequest;
  };

  signup(username: string): void {
    this.storage.set(this.HAS_LOGGED_IN, true);
    this.setUsername(username);
    this.events.publish('user:signup');
  };

  logout(): void {
    this.storage.remove(this.HAS_LOGGED_IN);
    this.storage.remove('username');
    this.events.publish('user:logout');
  };

  setUsername(username: string): void {
    this.storage.set('username', username);
  };

  getUsername(): Promise<string> {
    return this.storage.get('username').then((value) => {
      return value;
    });
  };

  hasLoggedIn(): Promise<boolean> {
    return this.storage.get(this.HAS_LOGGED_IN).then((value) => {
      return value === true;
    });
  };

  checkHasSeenTutorial(): Promise<string> {
    return this.storage.get(this.HAS_SEEN_TUTORIAL).then((value) => {
      return value;
    });
  };

  validateLogin(userName: string, password: string): SendRequest  {
    this.auth = new Auth(userName, "Web/Mobile", password, "IOS", "Mobile", "SDFSDKLGHASKLDFGHSAKLFG214ADFA",  "Member", "1.1", "aaabbbccc");
    
    this.loginRequestData = new LoginRequestData(this.auth);
    
    
    this.header= new Header("Login", "Authenticate", "None");

    
    this.request= new Request(this.header, this.loginRequestData);

    this.sendRequest= new SendRequest(this.request);


    console.log(this.request);
    console.log("registeration Service json data " +     JSON.stringify(this.sendRequest) + " url " + this.registrationUrl);
    console.log(JSON.stringify(this.sendRequest));
    
    return this.sendRequest;
    
  }

  

  /*submitMember(): Observable<MyResponse> {
  
  let headers = new Headers({ 'Content-Type': 'application/json' });
  let options = new RequestOptions({ headers: headers });
  return this.http
    .post(this.registrationUrl, JSON.stringify(this.sendRequest), options)
    .map(this.extractData)
    .catch(this.handleError);
 }*/

  /*submitMember(): Observable<MyResponse> {
  
  let headers = new Headers({ 'Content-Type': 'application/json' });
  return this.http
    .post(this.registrationUrl, JSON.stringify(this.sendRequest), {headers: headers})
    .subscribe(
        (response: Response) => {
          const data = response.json();
          console.log(data);
         },
        err => this.logError(err.json().message),
        () => console.log('Authentication Complete')
      );
  

 }*/

 logError(err) {
    console.error('There was an error: ' + err);
  }


  /*submitMember(): Promise<MyResponse> {
  
  let headers = new Headers({ 'Content-Type': 'application/json' });
  return this.http
    .post(this.registrationUrl, JSON.stringify(this.sendRequest), {headers: headers})
    .toPromise()
    .then(this.extractData)
    .catch(this.handleError);
  

 }*/

/*private extractData(res: Response) {
        this.MyResponse = res.json().MyResponse;
        console.log('while extractData RegisterationService' + this.MyResponse);
        return this.MyResponse || {};
    }

private handleError(error: Response) {
        console.error(error);
        return Observable.throw(error.json().error || 'Server Error');
    }
*/
}
