#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/types.h>
#include <linux/spi/spidev.h>
#include <limits.h>
#include <dlfcn.h>
#include <wiringPi.h>
#include <time.h>

static void pabort(const char *s)
{
	perror(s);
	abort();
}

static const char *lep3 = "/dev/spidev0.0";
static uint8_t mode;
static uint8_t bits = 8;
static uint32_t speed = 24000000;
static uint16_t delayy;

#define VOSPI_FRAME_SIZE (164)
uint8_t lepton_frame_packet[VOSPI_FRAME_SIZE];

int lepton3_1d[120*160];

void adjust()
{
	int i, j;
	int max_i, max_j;
	unsigned int maxval = 0;
	unsigned int minval = UINT_MAX;
	

	//printf("Calculating min/max values for proper scaling...\n");
	for (i = 0; i < 19200; i++)
	{
		if ((lepton3_1d[i] > maxval) && (lepton3_1d[i] != UINT_MAX))
		{
			maxval = lepton3_1d[i];
		}
		if ((lepton3_1d[i] < minval) && (lepton3_1d[i] != 0))
		{
			minval = lepton3_1d[i];
		}
	}
	for (i = 0; i < 19200; i++)
	{
		//lepton3_1d[i] -= minval;
	}

}


int transfer(int fd) {
	int ret;
	int frame_number;
	uint8_t tx[VOSPI_FRAME_SIZE] = {};
	struct spi_ioc_transfer tr = {
		.tx_buf = (unsigned long)tx,
		.rx_buf = (unsigned long)lepton_frame_packet,
		.len = VOSPI_FRAME_SIZE,
		.delay_usecs = delayy,
		.speed_hz = speed,
		.bits_per_word = bits,
	};

	int discard = 0;
	int segment = 1;
	while (segment < 5)
	{
		int packet = 0;
		while (packet < 60) 
		{
			ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr);
		
			if (ret < 1)
				pabort("can't send spi message");
			
			if ((lepton_frame_packet[0]&0xf) != 0x0f)
			{
				frame_number = lepton_frame_packet[1];
				if ((frame_number > 59))
				{
					// SYNC
					//if (discard > 1000) {
					
						wiringPiSetup();
						pinMode(1, OUTPUT);
						digitalWrite(1, HIGH);
						clock_t start_time = clock();
						printf("SYNC2\n");
						while (clock() < start_time + 200000);
						digitalWrite(1, LOW);
					
					//}
					discard ++;
					
					packet = 0;
					continue;
				}
				
				if ((frame_number == 20) && ((lepton_frame_packet[0] >> 4) != segment))
				{
					
					//if (discard > 1000) {
					/*
						wiringPiSetup();
						pinMode(1, OUTPUT);
						digitalWrite(1, HIGH);
						clock_t start_time = clock();
						printf("SYNC2\n");
						while (clock() < start_time + 200000);
						digitalWrite(1, LOW);
					*/
					//}
					discard ++;
					
					packet = 0;
					continue;
				}
				if (packet == frame_number)
				{
					for(int i=0;i<80;i++)
					{
						lepton3_1d[i + packet*80 + (segment-1)*4800] = ((lepton_frame_packet[2*i+4] << 8 | lepton_frame_packet[2*i+5]) >> 2);
					}

					packet ++;
					
				}
			}
			else
			{
				discard ++;
				
				if (discard > 20000)
				{
					// RESET
					
					wiringPiSetup();
				    pinMode(4, OUTPUT);
					digitalWrite(4, LOW);
					clock_t start_time = clock();
					printf("RESET2\n");
					while (clock() < start_time + 100000);
					digitalWrite(4, HIGH);
					while (clock() < start_time + 6000000);
					
					return 1;
				}
			}
		}
		segment ++;
	}
	return 0;
}


void check(int fd) {
	int ret = 0;
	
	if (fd < 0)
	{
		pabort("can't open device");
	}

	ret = ioctl(fd, SPI_IOC_WR_MODE, &mode);
	if (ret == -1)
	{
		pabort("can't set spi mode");
	}

	ret = ioctl(fd, SPI_IOC_RD_MODE, &mode);
	if (ret == -1)
	{
		pabort("can't get spi mode");
	}

	ret = ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &bits);
	if (ret == -1)
	{
		pabort("can't set bits per word");
	}

	ret = ioctl(fd, SPI_IOC_RD_BITS_PER_WORD, &bits);
	if (ret == -1)
	{
		pabort("can't get bits per word");
	}

	ret = ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &speed);
	if (ret == -1)
	{
		pabort("can't set max speed hz");
	}

	ret = ioctl(fd, SPI_IOC_RD_MAX_SPEED_HZ, &speed);
	if (ret == -1)
	{
		pabort("can't get max speed hz");
	}

	//printf("spi mode: %d\n", mode);
	//printf("bits per word: %d\n", bits);
	//printf("max speed: %d Hz (%d MHz)\n", speed, speed/1000000);
} 

int *lepton3(void) {
	int ret = 0;
	int fd;
	fd = open(lep3, O_RDWR);
	
	while (transfer(fd) != 0);
	check(fd);
	
	//transfer(fd);
	
	close(fd);
	adjust();

	return lepton3_1d;
}
