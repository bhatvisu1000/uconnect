import { MainArg } from "../MainArg";
export class LoginRequestData extends MainArg {
  constructor(public firstName: String, public lastName: String, public mobileNo: String, public zipCode: String, public emailAddress: String) {
	super();

  }
}
