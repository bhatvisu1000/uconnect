import { MainArg } from "../MainArg";
import { Auth } from "../connection/Auth";

export class LoginRequestData extends MainArg {
  constructor(public Auth: Auth) {
	super();

  }
}
