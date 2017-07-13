package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"flag"
	"github.com/gocarina/gocsv"
	"gopkg.in/yaml.v2"
	"io/ioutil"
	"path/filepath"
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

type Config struct {
	Twitory struct {
		Archive string `yaml:"archive"`
	}
}

var appConfig = Config{}

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

func getFileName(user string) (string, error) {
	fpath := "%s.csv"

	if len(user) == 0 {
		return fmt.Sprintf(fpath, "tweets"), nil
	}

	path := filepath.Join(appConfig.Twitory.Archive, fmt.Sprintf(fpath, user))

	if _, err := os.Stat(path); os.IsNotExist(err) {
		return "", errors.New("Not found tweets file")
	}

	return path, nil
}

func channelReader(user string) (chan *Tweet, error) {
	tweets := make(chan *Tweet)
	path, err := getFileName(user)
	if err != nil {
		return nil, err
	}

	go func() {
		tweetsFile, err := os.OpenFile(path, os.O_RDONLY, os.ModePerm)
		if err != nil {
			panic(err)
		}
		defer tweetsFile.Close()

		if err := gocsv.UnmarshalToChan(tweetsFile, tweets); err != nil {
			log.Printf("Error unmarshaling engine data: %v\n", err)
		}
	}()

	return tweets, nil
}

func simpleReader(user string) ([]*Tweet, error) {
	path, err := getFileName(user)
	if err != nil {
		return nil, err
	}

	tweetsFile, err := os.OpenFile(path, os.O_RDONLY, os.ModePerm)
	if err != nil {
		return nil, err
	}
	defer tweetsFile.Close()

	tweets := []*Tweet{}

	if err := gocsv.UnmarshalFile(tweetsFile, &tweets); err != nil {
		check(err)
	}

	return tweets, nil

}

func handler(w http.ResponseWriter, r *http.Request) {
	tsNow := DateTime{time.Now()}

	enc := json.NewEncoder(w)
	result := []*Tweet{}

	user := r.URL.Query().Get("user")

	tweets, err := channelReader(user)
	if err != nil {
		enc.Encode(map[string]interface{}{"status": "error", "error": err.Error()})
		return
	}
	for tweet := range tweets {
		if tsNow.isDay(tweet.Timestamp) {
			result = append(result, tweet)
		}

	}

	enc.Encode(map[string]interface{}{"status": "ok", "tweets": result})
}

func server() {
	http.HandleFunc("/tweets", handler)
	http.ListenAndServe(":8080", nil)
}

func main() {
	config := flag.String("config", "config.yaml", "Path to config.yaml")
	user := flag.String("user", "", "Test username for channel/simple")
	flag.Parse()

	cmd := "server"
	fargs := flag.Args()
	if len(fargs) >= 1 {
		cmd = fargs[0]
	}

	config_file, err := ioutil.ReadFile(*config)
	check(err)

	err = yaml.Unmarshal(config_file, &appConfig)
	check(err)

	if cmd == "server" {
		server()
		os.Exit(0)
	}

	i := 0
	switch cmd {
	case "channel":
		{
			tweets, err := channelReader(*user)
			check(err)
			for _ = range tweets {
				i++
			}
		}
	case "simple":
		{
			tweets, err := simpleReader(*user)
			check(err)
			for _ = range tweets {
				i++
			}
		}
	}

	fmt.Println("Read ", i, " rows")
}
