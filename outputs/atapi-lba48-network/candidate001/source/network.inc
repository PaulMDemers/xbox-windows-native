/* Bounded real TCP exchange through the emulated NIC; host verifies every byte. */
static void networkCheck(const char *label,DWORD phase) {
    WSADATA data;SOCKET s;static struct sockaddr_in address;
    fd_set writes;struct timeval timeout;int error,n,offset;
    DWORD round,i,ms=5000;static BYTE tx[4096],rx[4096];
    if(WSAStartup(MAKEWORD(2,0),&data))fatal("FAIL_WSA_START");
    {
        SOCKET listener=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
        if(listener==INVALID_SOCKET)fatal("FAIL_SOCKET");
        address.sin_family=AF_INET;address.sin_port=htons(4597);address.sin_addr.s_addr=INADDR_ANY;
        error=1;if(setsockopt(listener,SOL_SOCKET,SO_REUSEADDR,(char*)&error,sizeof(error)))fatal("FAIL_REUSE");
        if(bind(listener,(struct sockaddr*)&address,sizeof(address))||listen(listener,1))fatal("FAIL_LISTEN");
        FD_ZERO(&writes);FD_SET(listener,&writes);timeout.tv_sec=30;timeout.tv_usec=0;
        if(select(0,&writes,NULL,NULL,&timeout)!=1)fatal("FAIL_ACCEPT_WAIT");
        s=accept(listener,NULL,NULL);if(s==INVALID_SOCKET)fatal("FAIL_ACCEPT");
        if(closesocket(listener))fatal("FAIL_LISTENER_CLOSE");
    }
    if(setsockopt(s,SOL_SOCKET,SO_RCVTIMEO,(char*)&ms,sizeof(ms))||setsockopt(s,SOL_SOCKET,SO_SNDTIMEO,(char*)&ms,sizeof(ms)))fatal("FAIL_SOCKET_TIMEOUT");
    for(round=0;round<32;round++) {
        for(i=0;i<sizeof(tx);i++)tx[i]=(BYTE)(phase*97+round*13+i*7);
        offset=0;while(offset<(int)sizeof(tx)){n=send(s,(char*)tx+offset,sizeof(tx)-offset,0);if(n<=0)fatal("FAIL_SEND");offset+=n;}
        offset=0;while(offset<(int)sizeof(rx)){n=recv(s,(char*)rx+offset,sizeof(rx)-offset,0);if(n<=0)fatal("FAIL_RECV");offset+=n;}
        for(i=0;i<sizeof(rx);i++)if(rx[i]!=(BYTE)(tx[i]^0xa5))fatal("FAIL_NETWORK_BYTES");
    }
    if(shutdown(s,SD_SEND))fatal("FAIL_SOCKET_SHUTDOWN");
    if(recv(s,(char*)rx,1,0)!=0)fatal("FAIL_NETWORK_EOF");
    if(closesocket(s)||WSACleanup())fatal("FAIL_SOCKET_CLOSE");
    record(label,32,131072,131072);
}

