package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gocarina/gocsv"
)

/*
0 tweet_id
1 in_reply_to_status_id
2 in_reply_to_user_id
3 timestamp
4 source
5 text
6 retweeted_status_id
7 retweeted_status_user_id
8 retweeted_status_timestamp
9 expanded_urls
*/

type DateTime struct {
	time.Time
}

const DateFormat = "2006-01-02 15:04:05 -0700"

// Convert the internal date as CSV string
func (date *DateTime) MarshalCSV() (string, error) {
	return date.Time.Format(DateFormat), nil
}

// Convert the CSV string as internal date
func (date *DateTime) UnmarshalCSV(csv string) (err error) {
	date.Time, err = time.Parse(DateFormat, csv)
	if err != nil {
		return err
	}
	return nil
}

func (date DateTime) MarshalJSON() ([]byte, error) {
	s, _ := date.MarshalCSV()
	return json.Marshal(s)
}

func (date DateTime) isTimeDay(ts time.Time) bool {
	return date.Time.Day() == ts.Day() && date.Time.Month() == ts.Month()
}

func (date DateTime) isDay(dt DateTime) bool {
	return date.isTimeDay(dt.Time)
}

/*func (date DateTime) isDay(ts DateTime) bool {
	return date.isDay(ts.Time)
}*/

type Tweet struct {
	ID        string   `csv:"tweet_id" json:"tweet_id"`
	Text      string   `csv:"text" json:"text"`
	Timestamp DateTime `csv:"timestamp" json:"timestamp"`
	Source    string   `csv:"source" json:"source"`
}

func check(e error) {
	if e != nil {
		log.Fatal(e)
		panic(e)
	}
}

func channelReader() chan *Tweet {
	tweetsFile, err := os.OpenFile("tweets.csv", os.O_RDONLY, os.ModePerm)
	if err != nil {
		panic(err)
	}
	defer tweetsFile.Close()
	tweets := make(chan *Tweet)
	go func() {
		gocsv.UnmarshalToChan(tweetsFile, tweets)
		close(tweets)
	}()

	return tweets
}

func simpleReader() []*Tweet {
	tweetsFile, err := os.OpenFile("tweets.csv", os.O_RDONLY, os.ModePerm)
	if err != nil {
		panic(err)
	}
	defer tweetsFile.Close()

	tweets := []*Tweet{}

	if err := gocsv.UnmarshalFile(tweetsFile, &tweets); err != nil {
		check(err)
	}

	return tweets

}

func handler(w http.ResponseWriter, r *http.Request) {
	tsNow := DateTime{time.Now()}

	fmt.Println(tsNow.MarshalJSON())

	enc := json.NewEncoder(w)
	result := []*Tweet{}

	tweets := channelReader()
	for tweet := range tweets {
		if tsNow.isDay(tweet.Timestamp) {
			result = append(result, tweet)
		}

	}

	enc.Encode(result)

}

func server() {
	http.HandleFunc("/tweets", handler)
	http.ListenAndServe(":8080", nil)
}

func main() {
	if len(os.Args) == 1 {
		server()
		os.Exit(0)
	}
	i := 0

	if os.Args[1] == "server" {
		server()
	} else if os.Args[1] == "channel" {
		tweets := channelReader()
		fmt.Println("Read from channel", tweets)
		for _ = range tweets {
			i++
		}
	} else if os.Args[1] == "simple" {
		for _ = range simpleReader() {
			i++
		}
	}

	fmt.Println("Read ", i, " rows")
}
