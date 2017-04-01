import { Injectable } from "@angular/core";
import { Http, Response } from "@angular/http";
import {Observable} from 'rxjs/Observable';
import { Headers, RequestOptions } from '@angular/http';
import 'rxjs/Rx';

import {SendRequest} from "../models/SendRequest"
import {Request} from "../models/Request"
import {Header} from "../models/Header"
import {MainArg} from "../models/MainArg"
import {Address} from "../models/connection/Address"
import {Main} from "../models/connection/Main"
import {Contact} from "../models/connection/Contact"


@Injectable()
export class RegisterationService {
  private request: Request = null;
  private main: Main = null;
  private address: Address = null;
  private contact: Contact = null;
  private mainArg: MainArg = null;
  private header:  Header = null;
  private sendRequest: SendRequest = null;
  
  private registrationUrl = 'http://localhost:5000/processRequest/insert';
  constructor(private http: Http) {
  }

 createMember(firstName: string,
            lastName: string,
            mobileNo: string,
            zipCode: string,
            emailAddress: string) {
    this.main = new Main(firstName, lastName, "M");
    this.address = new Address("", "", "", zipCode, "", "");
    this.contact = new Contact(emailAddress, mobileNo, "N/A");
    
  
    this.mainArg = new MainArg(this.main, this.address, this.contact);
    this.header= new Header("RegisterMember_01", "CreateMember_01", "None");

    
    this.request= new Request(this.header, this.mainArg);

    this.sendRequest= new SendRequest(this.request);
    
    console.log("mainArg" + this.mainArg);
    console.log("main" + this.main);
    console.log("address" + this.address);
    console.log("contact" + this.contact);

    console.log(this.request);
    console.log("registeration Serive json data " +     JSON.stringify(this.sendRequest) + " url " + this.registrationUrl);
    console.log(JSON.stringify(this.sendRequest));
  }

  
 submitMember() {
  let headers = new Headers({ 'Content-Type': 'application/json' });
  return this.http
    .post(this.registrationUrl, JSON.stringify(this.sendRequest), {headers: headers})
    .toPromise()
    .then(res => res.json().data)
    .catch(this.handleError);
 }
private extractData(res: Response) {
        let body = res.json();
        console.log('while extractData RegisterationService' + body);
        return body.data || {};
    }
private handleError(error: Response) {
        console.error(error);
        return Observable.throw(error.json().error || 'Server Error');
    }

/**addProduct(product: Product) {                
        let body = JSON.stringify(product);            
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let options = new RequestOptions({ headers: headers });

        return this.http.post(this.productsUrl, body, options)
            .map(this.extractData)
            .catch(this.handleError);
    }

    private extractData(res: Response) {
        let body = res.json();
        return body.data || {};
    }

    private handleError(error: Response) {
        console.error(error);
        return Observable.throw(error.json().error || 'Server Error');
    }
*/
 }