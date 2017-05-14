import { Header } from "./Header";
import { MainArg } from "./MainArg";

export class MyResponse {
  constructor(public Header: Header, public MainArg: MainArg) {}
}