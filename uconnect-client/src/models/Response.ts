import { Header } from "./response/Header";
import { MainArg } from "./MainArg";

export class MyResponse {
  constructor(public Header: Header, public MainArg: MainArg) {}
}