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

// THIS IS THE CURRENT VERSION THAT WORKS


//#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))

static void pabort(const char *s)
{
	perror(s);
	abort();
}

//static const char *device = "/dev/spidev0.0";
static const char *lep2 = "/dev/spidev1.0";
static const char *lep3 = "/dev/spidev0.0";
static uint8_t mode;
static uint8_t bits = 8;
static uint32_t speed = 24000000;
static uint16_t delayy;

#define VOSPI_FRAME_SIZE (164)
uint8_t lepton_frame_packet[VOSPI_FRAME_SIZE];
static int lepton_image[60][80];

static int lepton2_image[60][80];
static int lepton3_image[120][160];
int lepton2_1d[60*80];
int lepton3_1d[120*160];

int seg_arr[120*160/4];

void sync(void) {
    // Initialize GPIO with BOARD numbering scheme
    wiringPiSetup();

    // Set pin 8 (CS pin) as output
    pinMode(8, OUTPUT);

    // Deassert chip select (set high)
    digitalWrite(8, HIGH);

    // Wait for 185 milliseconds
    usleep(185 * 1000);

    // Reassert chip select (set low)
    digitalWrite(8, LOW);
}


void adjust(int type)
{
	int i, j;
	int max_i, max_j;
	unsigned int maxval = 0;
	unsigned int minval = UINT_MAX;
	
	if (type == 2)
	{
		//printf("Calculating min/max values for proper scaling...\n");
		for(i=0;i<60;i++)
		{
			for(j=0;j<80;j++)
			{
				if (lepton2_image[i][j] > maxval) {
					maxval = lepton2_image[i][j];
				}
				if (lepton2_image[i][j] < minval) {
					minval = lepton2_image[i][j];
				}
			}
		}
		//printf("maxval = %u\n",maxval);
		//printf("minval = %u\n",minval);

		for(i=0;i<60;i++)
		{
			for(j=0;j<80;j++)
			{
				lepton2_image[i][j] -= minval;
			}
		}
	}
	else if (type == 3)
	{
		//printf("Calculating min/max values for proper scaling...\n");
		// assuming 1d array
		for (i = 0; i < 19200; i++)
		{
			if ((lepton3_1d[i] > maxval) && (lepton3_1d[i] != 0))
			{
				maxval = lepton3_1d[i];
			}
			if ((lepton3_1d[i] < minval) && (lepton3_1d[i] != 0))
			{
				minval = lepton3_1d[i];
			}
			//printf("maxval = %u\n",maxval);
			//printf("minval = %u\n",minval);
		}
		for (i = 0; i < 19200; i++)
		{
			lepton3_1d[i] -= minval;
		}
	} 
	else
	{
		fprintf(stderr, "incorrect type");
	}
}


int transfer(int fd)
{
	int ret;
	int i;
	int frame_number;
	uint8_t tx[VOSPI_FRAME_SIZE] = {0, };
	struct spi_ioc_transfer tr = {
		.tx_buf = (unsigned long)tx,
		.rx_buf = (unsigned long)lepton_frame_packet,
		.len = VOSPI_FRAME_SIZE,
		.delay_usecs = delayy,
		.speed_hz = speed,
		.bits_per_word = bits,
	};
	
	/*
	ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr);
	if (ret < 1)
		pabort("can't send spi message");

	if(((lepton_frame_packet[0]&0xf) != 0x0f))
	{
		frame_number = lepton_frame_packet[1];
		if(frame_number < 60 )
		{
			for(i=0;i<80;i++)
			{
				lepton2_image[frame_number][i] = (lepton_frame_packet[2*i+4] << 8 | lepton_frame_packet[2*i+5]);
			}
		}
	}
	return frame_number;
	*/
	
	// --------------------
	int discard = 0;
	int packet = 0;
	while (packet < 60) 
	{
		ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr);
		
		if (ret < 1)
			pabort("can't send spi message");
			
		if ((lepton_frame_packet[0]&0xf) != 0x0f)
		{
			frame_number = lepton_frame_packet[1];
			//printf("packet: %d\n", frame_number);
			if ((frame_number > 59) && (frame_number !=255))
			{
				sync();
				packet = 0;
				continue;
			}
			
			if (packet == frame_number)
			{
				//printf("packet: %d\n", packet);
				for(int i=0;i<80;i++)
				{
					lepton2_1d[i + packet*80] = ((lepton_frame_packet[2*i+4] << 8 | lepton_frame_packet[2*i+5]) >> 2);
				}

				packet ++;
				
			}
		}
		else 
		{
			discard ++;
			if (discard > 1000)
			{
				sync();
				printf("discard > 1000, sync... \n");
			}
		}
	}
	return 0;
	
}

int transferoni(int fd) {
	int ret;
	int frame_number;
	uint8_t tx[VOSPI_FRAME_SIZE] = {0, };
	struct spi_ioc_transfer tr = {
		.tx_buf = (unsigned long)tx,
		.rx_buf = (unsigned long)lepton_frame_packet,
		.len = VOSPI_FRAME_SIZE,
		.delay_usecs = delayy,
		.speed_hz = speed,
		.bits_per_word = bits,
	};

	
	int segment = 1;
	int discard = 0;
	while (segment < 5)
	{
		//printf("segment: %d\n", segment);
		int packet = 0;
		while (packet < 60) 
		{
			ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr);
		
			if (ret < 1)
				pabort("can't send spi message");
			
			if ((lepton_frame_packet[0]&0xf) != 0x0f) // discard
			{
				frame_number = lepton_frame_packet[1];
				//printf("packet: %d\n", frame_number);
				if ((frame_number > 59) && (frame_number !=255))
				{
					printf("a\n");
					sync();
					packet = 0;
					continue;
				}
				
				if ((frame_number == 20) && ((lepton_frame_packet[0] >> 4) != segment))
				{
					//printf("segment: %d\n", lepton_frame_packet[0] >> 4);
					printf("b\n");
					sync();
					packet = 0;
					continue;
				}
				if (packet == frame_number)
				{
					//printf("packet: %d\n", packet);
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
				if (discard > 1000)
				{
					sync();
					printf("discard > 1000, sync... \n");
				}
			}
		}
		segment ++;
	}
	//printf("discard: %d\n", discard);
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



int *lepton2(void) {
	int fd;
	
	fd = open(lep2, O_RDWR);
	
	check(fd);
	
	printf("stuck two???\n");
	//while(transfer(fd)!=59){}
	transfer(fd);
	
	close(fd);
	adjust(2);

	// one dim array
	/*
	int e = 0;
	for (int i = 0; i < 60; i++) {
		for (int j = 0; j < 80; j++) {
			lepton2_1d[e++] = lepton2_image[i][j];
		}
	}
	*/

	return lepton2_1d;
}

int *lepton3(void) {
	int ret = 0;
	int fd;
	
	fd = open(lep3, O_RDWR);
	printf("fd: %d\n", fd);
	check(fd);
	printf("stuck three???\n");
	transferoni(fd);
	
	close(fd);
	adjust(3);

	return lepton3_1d;
}
