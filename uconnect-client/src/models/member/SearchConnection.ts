import { MainArg } from "../MainArg";
import { Auth } from "../connection/Auth";

export class SearchConnection extends MainArg {
  constructor(public SearchCriteria: String, public Page: String, public Auth: Auth) {
	super();

  }
}
