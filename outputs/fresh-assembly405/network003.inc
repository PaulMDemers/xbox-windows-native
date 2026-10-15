/* Scoped loopback-forward TCP witness, not an Internet connectivity test. */
static DWORD network(void) {
    WSADATA wd; SOCKET listener=INVALID_SOCKET,s=INVALID_SOCKET;
    struct sockaddr_in address; fd_set reads; struct timeval wait;
    BYTE tx[4096],rx[4096]; DWORD round,i,ms=5000,result=1;
    int n,at;
    if(WSAStartup(MAKEWORD(2,0),&wd))return 1;
    listener=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);if(listener==INVALID_SOCKET)goto done;
    zero(&address,sizeof(address));address.sin_family=AF_INET;
    address.sin_addr.s_addr=INADDR_ANY;address.sin_port=htons(4597);
    if(bind(listener,(struct sockaddr*)&address,sizeof(address))||listen(listener,1)){result=2;goto done;}
    FD_ZERO(&reads);FD_SET(listener,&reads);wait.tv_sec=45;wait.tv_usec=0;
    if(select(0,&reads,0,0,&wait)!=1){result=3;goto done;}
    s=accept(listener,0,0);if(s==INVALID_SOCKET){result=4;goto done;}
    if(setsockopt(s,SOL_SOCKET,SO_RCVTIMEO,(char*)&ms,sizeof(ms))||setsockopt(s,SOL_SOCKET,SO_SNDTIMEO,(char*)&ms,sizeof(ms))){result=5;goto done;}
    if(send(s,"XWN405-NET1\n",12,0)!=12){result=6;goto done;}
    for(round=0;round<32;round++){
        for(i=0;i<sizeof(tx);i++)tx[i]=(BYTE)(97+round*13+i*7);
        at=0;while(at<(int)sizeof(tx)){n=send(s,(char*)tx+at,sizeof(tx)-at,0);if(n<=0){result=7;goto done;}at+=n;}
        at=0;while(at<(int)sizeof(rx)){n=recv(s,(char*)rx+at,sizeof(rx)-at,0);if(n<=0){result=8;goto done;}at+=n;}
        for(i=0;i<sizeof(rx);i++)if(rx[i]!=(BYTE)(tx[i]^0xa5)){result=9;goto done;}
    }
    if(shutdown(s,SD_SEND)||recv(s,(char*)rx,1,0)!=0){result=10;goto done;}
    result=0;
done:
    if(s!=INVALID_SOCKET)closesocket(s);
    if(listener!=INVALID_SOCKET)closesocket(listener);
    WSACleanup();return result;
}
